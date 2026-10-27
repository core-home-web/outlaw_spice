"""Upscale the transparent jar cutouts 4x with Real-ESRGAN (x4plus), for the homepage slider.

Needs PyTorch and the RealESRGAN_x4plus.pth weights
(https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth):

    python3 tools/upscale_cutouts.py path/to/RealESRGAN_x4plus.pth

Reads brand-assets/products/cutouts/<id>.avif, writes brand-assets/products/cutouts-4x/<id>.webp.
Colour goes through the model; the alpha mask is resized with Lanczos so the jar's
silhouette stays exactly as cut. Then run tools/optimize_images.py to make the web copies.
"""
import sys
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torch import nn
from torch.nn import functional as F

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "brand-assets" / "products" / "cutouts"
OUT = ROOT / "brand-assets" / "products" / "cutouts-4x"


# --- RRDBNet, the Real-ESRGAN generator (same layer names as the released weights) ---
class ResidualDenseBlock(nn.Module):
    def __init__(self, nf=64, gc=32):
        super().__init__()
        self.conv1 = nn.Conv2d(nf, gc, 3, 1, 1)
        self.conv2 = nn.Conv2d(nf + gc, gc, 3, 1, 1)
        self.conv3 = nn.Conv2d(nf + 2 * gc, gc, 3, 1, 1)
        self.conv4 = nn.Conv2d(nf + 3 * gc, gc, 3, 1, 1)
        self.conv5 = nn.Conv2d(nf + 4 * gc, nf, 3, 1, 1)
        self.lrelu = nn.LeakyReLU(0.2, inplace=True)

    def forward(self, x):
        x1 = self.lrelu(self.conv1(x))
        x2 = self.lrelu(self.conv2(torch.cat((x, x1), 1)))
        x3 = self.lrelu(self.conv3(torch.cat((x, x1, x2), 1)))
        x4 = self.lrelu(self.conv4(torch.cat((x, x1, x2, x3), 1)))
        x5 = self.conv5(torch.cat((x, x1, x2, x3, x4), 1))
        return x5 * 0.2 + x


class RRDB(nn.Module):
    def __init__(self, nf, gc=32):
        super().__init__()
        self.rdb1 = ResidualDenseBlock(nf, gc)
        self.rdb2 = ResidualDenseBlock(nf, gc)
        self.rdb3 = ResidualDenseBlock(nf, gc)

    def forward(self, x):
        return self.rdb3(self.rdb2(self.rdb1(x))) * 0.2 + x


class RRDBNet(nn.Module):
    def __init__(self, nf=64, nb=23, gc=32):
        super().__init__()
        self.conv_first = nn.Conv2d(3, nf, 3, 1, 1)
        self.body = nn.Sequential(*[RRDB(nf, gc) for _ in range(nb)])
        self.conv_body = nn.Conv2d(nf, nf, 3, 1, 1)
        self.conv_up1 = nn.Conv2d(nf, nf, 3, 1, 1)
        self.conv_up2 = nn.Conv2d(nf, nf, 3, 1, 1)
        self.conv_hr = nn.Conv2d(nf, nf, 3, 1, 1)
        self.conv_last = nn.Conv2d(nf, 3, 3, 1, 1)
        self.lrelu = nn.LeakyReLU(0.2, inplace=True)

    def forward(self, x):
        feat = self.conv_first(x)
        feat = feat + self.conv_body(self.body(feat))
        feat = self.lrelu(self.conv_up1(F.interpolate(feat, scale_factor=2, mode="nearest")))
        feat = self.lrelu(self.conv_up2(F.interpolate(feat, scale_factor=2, mode="nearest")))
        return self.conv_last(self.lrelu(self.conv_hr(feat)))


def upscale_rgb(model, rgb, tile=200, pad=12):
    """4x upscale in overlapping tiles to keep memory flat."""
    x = torch.from_numpy(np.asarray(rgb, dtype=np.float32) / 255.0).permute(2, 0, 1)[None]
    _, _, h, w = x.shape
    out = torch.zeros(1, 3, h * 4, w * 4)
    with torch.inference_mode():
        for y0 in range(0, h, tile):
            for x0 in range(0, w, tile):
                y1, x1 = min(y0 + tile, h), min(x0 + tile, w)
                py0, px0 = max(y0 - pad, 0), max(x0 - pad, 0)
                py1, px1 = min(y1 + pad, h), min(x1 + pad, w)
                res = model(x[:, :, py0:py1, px0:px1])
                oy, ox = (y0 - py0) * 4, (x0 - px0) * 4
                out[:, :, y0 * 4:y1 * 4, x0 * 4:x1 * 4] = res[:, :, oy:oy + (y1 - y0) * 4, ox:ox + (x1 - x0) * 4]
    arr = (out[0].permute(1, 2, 0).clamp(0, 1).numpy() * 255).round().astype(np.uint8)
    return Image.fromarray(arr)


def main(weights):
    torch.set_num_threads(max(1, torch.get_num_threads()))
    model = RRDBNet()
    state = torch.load(weights, map_location="cpu", weights_only=True)
    model.load_state_dict(state.get("params_ema", state), strict=True)
    model.eval()
    OUT.mkdir(parents=True, exist_ok=True)
    for src in sorted(SRC.glob("*.avif")):
        im = Image.open(src).convert("RGBA")
        alpha = im.getchannel("A")
        # Fill transparent pixels with the nearby jar colour so edges don't pick up junk.
        rgb = Image.new("RGB", im.size, (40, 36, 34))
        rgb.paste(im.convert("RGB"), mask=alpha)
        big = upscale_rgb(model, rgb)
        big.putalpha(alpha.resize(big.size, Image.LANCZOS))
        big.save(OUT / f"{src.stem}.webp", "WEBP", quality=95, method=6)
        print(src.stem, big.size, flush=True)


if __name__ == "__main__":
    main(sys.argv[1])
