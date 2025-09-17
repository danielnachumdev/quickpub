import logging

from ...upload_target import UploadTarget

logger = logging.getLogger(__name__)

class GithubUploadTarget(UploadTarget):
    def upload(self, version: str, **kwargs) -> None: # type: ignore
        from quickpub.proxy import cm
        from quickpub.enforcers import exit_if
        
        logger.info(f"Starting GitHub upload for version '{version}'")
        
        if self.verbose:
            logger.info("Staging files for Git commit")
        
        ret, stdout, stderr = cm("git add .")
        if ret != 0:
            logger.error(f"Git add failed with return code {ret}: {stderr.decode(encoding='utf8')}")
            exit_if(ret != 0, stderr.decode(encoding="utf8"))
        
        if self.verbose:
            logger.info(f"Committing changes with message 'updated to version {version}'")
        
        ret, stdout, stderr = cm(f"git commit -m \"updated to version {version}\"")
        if ret != 0:
            logger.error(f"Git commit failed with return code {ret}: {stderr.decode(encoding='utf8')}")
            exit_if(ret != 0, stderr.decode(encoding="utf8"))
        
        if self.verbose:
            logger.info("Pushing changes to GitHub")
        
        ret, stdout, stderr = cm("git push")
        if ret != 0:
            logger.error(f"Git push failed with return code {ret}: {stderr.decode(encoding='utf8')}")
            exit_if(ret != 0, stderr.decode(encoding="utf8"))
        
        logger.info(f"Successfully uploaded version '{version}' to GitHub")


__all__ = [
    "GithubUploadTarget",
]
