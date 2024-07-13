import asyncio
import logging
from pathlib import Path

import aiofiles
import aioshutil
import httpx

DOWNLOAD_LINK = "https://github.com/GyanD/codexffmpeg/releases/download/2024-07-10-git-1a86a7a48d/ffmpeg-2024-07-10-git-1a86a7a48d-full_build.zip"
logger = logging.getLogger(__name__)


class Setup:
    def __init__(self, http_client: httpx.AsyncClient) -> None:
        self.http_client = http_client
        self.download_url = DOWNLOAD_LINK
        self.download_path = Path("ffmpeg/ffmpeg.zip")

        self.download_path.parent.mkdir(exist_ok=True)

    async def download(self) -> None:
        logger.debug(f"Downloading {self.download_url}")
        async with self.http_client.stream("GET", url=self.download_url) as resp:
            resp.raise_for_status()
            async with aiofiles.open(self.download_path, mode="wb") as file:
                async for data in resp.aiter_bytes():
                    await file.write(data)

    async def unzip(self) -> None:
        logger.debug("Unziping {self.download_path} to {self.download_path.parent}")
        try:
            await aioshutil.unpack_archive(
                self.download_path, self.download_path.parent
            )
            self.download_path.unlink()
        except Exception:
            await aioshutil.rmtree(self.download_path.parent)
            raise ValueError("Bad Zipfile")

    async def move(self) -> None:
        logger.debug(f"Moving binaries to {self.download_path.parent}")
        dir = self.download_path.parent.iterdir().__next__()
        bin_dir = Path(f"{dir}/bin")
        for bin in bin_dir.iterdir():
            await aioshutil.move(bin, self.download_path.parent)
        await aioshutil.rmtree(dir)


async def main():
    async with httpx.AsyncClient(follow_redirects=True) as client:
        setup = Setup(client)
        await setup.download()
        await setup.unzip()
        await setup.move()


if __name__ == "__main__":
    asyncio.run(main())
