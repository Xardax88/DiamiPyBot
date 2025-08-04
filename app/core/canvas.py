import os
from PIL import Image, ImageDraw, ImageOps, ImageFont, ImageFilter
import requests
import io

import logging

logger = logging.getLogger(__name__)

FONT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "assets",
    "fonts",
    "Helvetica Neue Condensed Bold.ttf",
)


class CanvasRank:
    """
    Clase para generar imágenes de rank personalizadas para usuarios.
    Por ahora, solo genera una imagen de 880x300 px con bordes redondeados y fondo gris.
    """

    def __init__(
        self,
        guild_id: int,
        user_id: int,
        avatar_url: str,
        user_name: str = "Usuario",
        role: str = "User",
        exp: int = 0,
        level: int = 1,
        next_level_exp: int = 200,
        previous_level_exp: int = 0,
    ):
        """
        Inicializa la clase con el ID del usuario.
        :param
        guild_id: ID del servidor (guild).
        user_id: ID del usuario.
        avatar_url: URL del avatar del usuario.
        user_name: Nombre del usuario (opcional, por defecto "Usuario").
        role: Rol del usuario (opcional, por defecto "User").
        exp: Experiencia del usuario (opcional, por defecto 0).
        level: Nivel del usuario (opcional, por defecto 1).
        next_level_exp: Experiencia necesaria para el siguiente nivel (opcional, por defecto 200).
        previous_level_exp: Experiencia acumulada hasta el inicio del nivel actual (opcional por defecto 0).
        """
        self.guild_id = guild_id
        self.user_id = user_id
        self.user_name = user_name
        self.role = role
        self.exp = exp
        self.level = level
        self.avatar_url = avatar_url
        self.next_level_exp = next_level_exp
        self.previous_level_exp = previous_level_exp

        self.width = 880
        self.height = 300
        self.radius = 40
        self.border_gradient_0 = (252, 185, 105)  # #fcb969
        self.border_gradient_1 = (226, 97, 36)  # #e26124
        self.inner_gradient_0 = (50, 50, 50)
        self.inner_gradient_1 = (60, 60, 60)
        self.avatar_size = 240

    def get_avatar(self, avatar_url: str) -> Image.Image:
        """
        Descarga el avatar del usuario, lo redimensiona y le aplica bordes redondeados.
        :param avatar_url: URL del avatar del usuario.
        :return: Imagen PIL.Image del avatar procesado.
        """
        response = requests.get(avatar_url)
        avatar = Image.open(io.BytesIO(response.content)).convert("RGBA")
        avatar = avatar.resize((self.avatar_size, self.avatar_size), Image.LANCZOS)
        # Crear máscara circular
        mask = Image.new("L", (self.avatar_size, self.avatar_size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, self.avatar_size, self.avatar_size), fill=255)
        avatar = ImageOps.fit(
            avatar, (self.avatar_size, self.avatar_size), centering=(0.5, 0.5)
        )
        avatar.putalpha(mask)
        return avatar

    def render(self) -> Image.Image:
        """
        Genera y retorna la imagen del rank con todos los elementos visuales
        :return: Imagen PIL.Image
        """
        # Crear imagen con fondo transparente
        img = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))

        # --- Gradiente exterior (borde)---
        gradient = Image.new("RGBA", (self.width, self.height), 0)
        draw_gradient = ImageDraw.Draw(gradient)
        start_color = self.border_gradient_0
        end_color = self.border_gradient_1
        for x in range(self.width):
            ratio = x / (self.width - 1)
            r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
            g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
            b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
            draw_gradient.line([(x, 0), (x, self.height)], fill=(r, g, b, 255))

        # Máscara para bordes redondeados exteriores
        mask = Image.new("L", (self.width, self.height), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle(
            [(0, 0), (self.width, self.height)], radius=self.radius, fill=255
        )
        img.paste(gradient, (0, 0), mask)

        # --- Rectángulo interior ---
        margin = 10
        inner_width = self.width - 2 * margin
        inner_height = self.height - 2 * margin
        inner_radius = self.radius - 10 if self.radius > 10 else self.radius
        # Crear gradiente vertical de gris claro a gris oscuro
        inner_gradient = Image.new("RGBA", (inner_width, inner_height), 0)
        draw_inner = ImageDraw.Draw(inner_gradient)
        start_gray = self.inner_gradient_0
        end_gray = self.inner_gradient_1
        for y in range(inner_height):
            ratio = y / (inner_height - 1)
            r = int(start_gray[0] * (1 - ratio) + end_gray[0] * ratio)
            g = int(start_gray[1] * (1 - ratio) + end_gray[1] * ratio)
            b = int(start_gray[2] * (1 - ratio) + end_gray[2] * ratio)
            draw_inner.line([(0, y), (inner_width, y)], fill=(r, g, b, 255))
        # Máscara para bordes redondeados interiores
        inner_mask = Image.new("L", (inner_width, inner_height), 0)
        inner_mask_draw = ImageDraw.Draw(inner_mask)
        inner_mask_draw.rounded_rectangle(
            [(0, 0), (inner_width, inner_height)], radius=inner_radius, fill=255
        )
        img.paste(inner_gradient, (margin, margin), inner_mask)

        # --- Avatar del usuario ---
        if self.avatar_url:
            avatar_img = self.get_avatar(self.avatar_url)
            avatar_y = (self.height - self.avatar_size) // 2
            img.paste(avatar_img, (40, avatar_y), avatar_img)

        # --- Nombre de usuario ---
        if self.user_name:
            # Dibujar sombra del texto
            blurred = Image.new("RGBA", img.size)
            draw = ImageDraw.Draw(blurred)
            text = self.user_name
            # Cargar fuente (usar una fuente del sistema o del proyecto)
            try:
                font = ImageFont.truetype(FONT_PATH, 70)
            except IOError:
                logging.critical(
                    f"ADVERTENCIA: No se encontró la fuente en {FONT_PATH}. Usando fuente predeterminada.",
                    extra={"guild_id": self.guild_id},
                )
                font = ImageFont.load_default(size=70)

            # Medir el tamaño del texto
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            # El texto comienza exactamente a 240px del margen izquierdo
            x = 300
            # Centrado vertical respecto a la imagen
            y = (self.height - text_height - 60) / 2 - bbox[1]
            draw.text((x, y), text, font=font, fill=(0, 0, 0, 255))
            blurred = blurred.filter(ImageFilter.BoxBlur(7))
            img.paste(blurred, blurred)

            # Dibujar Nombre de usuario
            draw = ImageDraw.Draw(img)
            text = self.user_name
            # Cargar fuente (usar una fuente del sistema o del proyecto)
            try:
                font = ImageFont.truetype(FONT_PATH, 70)
            except IOError:
                logging.critical(
                    f"ADVERTENCIA: No se encontró la fuente en {FONT_PATH}. Usando fuente predeterminada.",
                    extra={"guild_id": self.guild_id},
                )
                font = ImageFont.load_default(size=70)

            draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))

        # --- Barra de experiencia ---

        # Calcular el ancho de la barra de experiencia
        bar_width = 550
        bar_height = 35
        bar_x = 300
        bar_y = (self.height - bar_height) // 2 + 40

        # Fondo de la barra de experiencia
        bar = Image.new("RGBA", (bar_width, bar_height), (0, 0, 0, 0))
        draw_bar = ImageDraw.Draw(bar)
        # Dibujar fondo de la barra
        draw_bar.rounded_rectangle(
            [(0, 0), (bar_width, bar_height)],
            radius=bar_height // 3,
            fill=(0, 0, 0, 200),
        )
        img.paste(bar, (bar_x, bar_y), bar)

        # Barra de progreso de experiencia
        exp_bar = self.exp - self.previous_level_exp
        progress_width = int((exp_bar / self.next_level_exp) * bar_width)
        progress = Image.new("RGBA", (progress_width, bar_height), (0, 0, 0, 0))
        draw_progress = ImageDraw.Draw(progress)
        # Dibujar barra de progreso
        draw_progress.rounded_rectangle(
            [(0, 0), (progress_width, bar_height)],
            radius=bar_height // 3,
            fill=(252, 185, 105, 255),  # Color de la barra de progreso
        )
        img.paste(progress, (bar_x, bar_y), progress)

        # Fondo texto de nivel y experiencia
        bg_width = 380
        bg_height = 30
        bg_x = 300
        bg_y = (self.height - (bg_height // 2)) - 40

        # Fondo de la barra de experiencia
        bg = Image.new("RGBA", (bg_width, bg_height), (0, 0, 0, 0))
        draw_bg = ImageDraw.Draw(bg)
        # Dibujar fondo de la barra
        draw_bg.rounded_rectangle(
            [(0, 0), (bg_width, bg_height)],
            radius=bg_height // 3,
            fill=(0, 0, 0, 200),
        )
        img.paste(bg, (bg_x, bg_y), bg)

        # Texto de nivel y experiencia
        draw = ImageDraw.Draw(img)
        text_exp = f"{self.exp} / {self.next_level_exp} XP"
        text_level = f"Lvl {self.level}"
        # Cargar fuente (usar una fuente del sistema o del proyecto)
        try:
            font = ImageFont.truetype(FONT_PATH, 20)
        except IOError:
            logging.critical(
                f"ADVERTENCIA: No se encontró la fuente en {FONT_PATH}. Usando fuente predeterminada.",
                extra={"guild_id": self.guild_id},
            )
            font = ImageFont.load_default(size=20)

        # Medir el tamaño del texto
        bbox = draw.textbbox((0, 0), text_exp, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        # El texto comienza exactamente a 255px del margen izquierdo
        x = 310
        y = (self.height - text_height) - 40
        draw.text((x, y), text_exp, font=font, fill=(255, 255, 255, 255))
        bbox = draw.textbbox((0, 0), text_level, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (310 + bg_width) - text_width - 15
        draw.text((x, y), text_level, font=font, fill=(142, 126, 194, 255))

        # Fondo user type (User, Bot, Admin, Mod)
        bg_width = 160
        bg_height = 30
        bg_x = 690
        bg_y = (self.height - (bg_height // 2)) - 40
        bg = Image.new("RGBA", (bg_width, bg_height), (0, 0, 0, 0))
        draw_bg = ImageDraw.Draw(bg)
        # Dibujar fondo de la barra
        draw_bg.rounded_rectangle(
            [(0, 0), (bg_width, bg_height)],
            radius=bg_height // 3,
            fill=(0, 0, 0, 200),
        )
        img.paste(bg, (bg_x, bg_y), bg)

        # Texto de tipo de usuario
        draw = ImageDraw.Draw(img)
        role = f"{self.role}"
        # Cargar fuente (usar una fuente del sistema o del proyecto)
        try:
            font = ImageFont.truetype(FONT_PATH, 20)
        except IOError:
            logging.critical(
                f"ADVERTENCIA: No se encontró la fuente en {FONT_PATH}. Usando fuente predeterminada.",
                extra={"guild_id": self.guild_id},
            )
            font = ImageFont.load_default(size=20)

        # Medir el tamaño del texto
        bbox = draw.textbbox((0, 0), role, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = bg_x + (bg_width // 2) - (text_width // 2)
        y = (self.height - text_height) - 40
        draw.text((x, y), role, font=font, fill=(255, 255, 255, 255))

        return img
