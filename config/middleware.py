import os
import re
import rjsmin
import json

from servestatic.middleware import ServeStaticMiddleware

from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils.deprecation import MiddlewareMixin


class MinifyHTMLMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if "text/html" in response.get("Content-Type", ""):
            content = response.content.decode("utf-8")
            response.content = self.minify_html(content)
            response["Content-Length"] = str(len(response.content))
        return response

    def minify_html(self, html):
        # Divides non-sript and style types into segments
        segments = re.split(
            r"(<script.*?>.*?</script>|<style.*?>.*?</style>)",
            html,
            flags=re.DOTALL | re.IGNORECASE,
        )
        for i, segment in enumerate(segments):
            if i % 2 == 0:
                segments[i] = self._minify_non_script_style(segment)
            else:
                # Minify JS content only inside <script> tags
                if segment.lower().startswith("<script"):
                    segments[i] = self._minify_script(segment)
        return "".join(segments)

    def _minify_script(self, script_tag):
        # Extract JS code from <script> tag
        js_content = re.search(r"(?<=>)(.*?)(?=</script>)", script_tag, flags=re.DOTALL)
        if js_content:
            js_code = js_content.group(1)
            minified_js = rjsmin.jsmin(js_code)
            return script_tag.replace(js_code, minified_js)
        return script_tag

    def _minify_non_script_style(self, html_part):
        # Remove HTML comments (except IE conditional ones)
        html_part = re.sub(r"<!--(?!\[if).*?-->", "", html_part, flags=re.DOTALL)
        # Remove spaces between HTML tags
        html_part = re.sub(r">\s+<", "><", html_part)
        # Remove spaces around equal signs in attributes
        html_part = re.sub(r"\s*=\s*", "=", html_part)
        # Remove redundant boolean attributes
        html_part = re.sub(r'\b(\w+)=["\']\1["\']', r"\1", html_part)
        # Remove whitespace inside inline JS and CSS (e.g., style attributes or event handlers)
        html_part = re.sub(r"\s*{\s*", "{", html_part)
        html_part = re.sub(r"\s*}\s*", "}", html_part)
        html_part = re.sub(r"\s*;\s*", ";", html_part)
        # Flatten into one line and remove extra whitespace
        html_part = re.sub(r"\s+", " ", html_part).strip()
        return html_part


class CustomServeStaticMiddleware(ServeStaticMiddleware):
    """
    Custom version of CustomServeStaticMiddleware
    for serving '.png', '.jpg', and '.jpeg' as '.webp'
    with a fallback
    """

    IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Load the manifest to map original names to hashed names
        self.manifest = self.load_manifest()

    def load_manifest(self):
        if staticfiles_storage.manifest_name and staticfiles_storage.exists(
            staticfiles_storage.manifest_name
        ):
            with staticfiles_storage.open(staticfiles_storage.manifest_name) as f:
                return json.load(f)
        return {"paths": {}}

    async def __call__(self, request):
        accept = request.headers.get("Accept", "")
        client_accepts_webp = "image/webp" in accept
        path_info = request.path_info.replace("/static/", "")

        # Attempt to find the WebP version using the original filename
        original_name = self.get_original_name(path_info)
        if client_accepts_webp and original_name:
            webp_original_name = os.path.splitext(original_name)[0] + ".webp"
            webp_hashed_name = self.manifest["paths"].get(webp_original_name)
            if webp_hashed_name:
                # Serve the hashed WebP file
                lookup_key = f"{self.static_prefix}{webp_hashed_name}"
                static_file = self.files.get(lookup_key)
                if static_file:
                    return await self.aserve(static_file, request)

        # Fallback to original logic
        return await super().__call__(request)

    def get_original_name(self, hashed_path):
        # Reverse lookup to find the original filename from the hashed path
        for original, hashed in self.manifest.get("paths", {}).items():
            if hashed == hashed_path:
                return original
        return None
