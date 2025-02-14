import os
import json
import shutil
from io import BytesIO
from django.core.files.base import ContentFile
from servestatic.storage import (
    CompressedManifestStaticFilesStorage as BaseManifestStaticFilesStorage,
)

try:
    from PIL import Image
except ImportError:
    pass


class CompressedManifestStaticFilesStorage(BaseManifestStaticFilesStorage):
    def post_process(self, *args, **kwargs):
        # Convert Generator into list
        files = list(super().post_process(*args, **kwargs))
        # Create a new list of '.webp' files
        webp_entries = {}

        for original_name, hashed_name, processed in files:
            if not isinstance(processed, Exception) and self._is_image(original_name):
                webp_name = self._get_webp_name(original_name)
                webp_content = self._generate_webp(original_name)
                if webp_content:
                    # Save the hashed WebP file.
                    content_file_hashed = ContentFile(webp_content)
                    hashed_webp = self.hashed_name(webp_name, content_file_hashed)
                    self._save(hashed_webp, content_file_hashed)

                    # Determine the clean (unhashed) name.
                    clean_webp = self.clean_name(webp_name)
                    # Get the full file paths.
                    hashed_path = self.path(hashed_webp)
                    clean_path = self.path(clean_webp)
                    # Ensure the directory for the clean file exists.
                    os.makedirs(os.path.dirname(clean_path), exist_ok=True)
                    # Copy the hashed file to the clean path if it doesn't exist.
                    # if not os.path.exists(clean_path):
                    try:
                        shutil.copyfile(hashed_path, clean_path)
                    except Exception as e:
                        print(f"Error copying the hashed file: {e}")

                    # In our manifest, map the clean WebP name to the hashed file.
                    webp_entries[self.clean_name(webp_name)] = hashed_webp

        # Update hashed_files' paths in manifest ({"paths": {...}, ...})
        self.hashed_files.update(webp_entries)

        manifest = {}
        current = self.read_manifest()
        if current:
            try:
                manifest = json.loads(current)
            except Exception:
                manifest = {}

        manifest["paths"] = self.hashed_files
        manifest["stats"] = self.stat_static_root()

        new = json.dumps(manifest).encode()

        manifest_storage = getattr(self, "manifest_storage", self)
        manifest_storage.delete(self.manifest_name)
        manifest_storage._save(self.manifest_name, ContentFile(new))

        yield from files

    def _is_image(self, name):
        """Checks whether a file is of '.png', '.jpg', or '.jpeg' format"""
        ext = os.path.splitext(name)[1].lower()
        return ext in (".png", ".jpg", ".jpeg")

    def _get_webp_name(self, name):
        """Returns a filename with '.webp' format"""
        return os.path.splitext(name)[0] + ".webp"

    def _generate_webp(self, name):
        """Generates a '.webp' file using ''pillow'"""
        try:
            with self.open(name) as f:
                image = Image.open(f)
                output = BytesIO()
                image.save(output, format="WEBP")
                return output.getvalue()
        except Exception:
            return None
