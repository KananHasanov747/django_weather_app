import re
import rjsmin
from django.utils.deprecation import MiddlewareMixin


class MinifyHTMLMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if "text/html" in response.get("Content-Type", ""):
            content = response.content.decode("utf-8")
            response.content = self.minify_html(content)
            response["Content-Length"] = str(len(response.content))
        return response

    def minify_html(self, html):
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
