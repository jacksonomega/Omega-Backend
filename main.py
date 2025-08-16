from fastapi import FastAPI, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import EmailStr
import smtplib
from email.message import EmailMessage
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 465
    SMTP_USER: str = "jackson0102almeida@gmail.com"
    SMTP_PASS: str = "bfhr greh sjny ialm"

    class Config:
        env_file = ".env"

settings = Settings()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"]
)


def send_email_sync(subject: str, name: str, email: str, message: str):
    msg = EmailMessage()
    plain = (
        f"Nuevo mensaje de contacto\n\n"
        f"Nombre: {name}\n"
        f"Email: {email}\n\n"
        "Mensaje:\n"
        f"{message}\n"
    )
    msg.set_content(plain)

    # Versión HTML para clientes que la soporten
    html = f"""\
    <html>
        <body>
        <h2>Nuevo mensaje de contacto</h2>
        <p><strong>Nombre:</strong> {name}<br>
            <strong>Email:</strong> <a href="mailto:{email}">{email}</a></p>
        <hr>
        <h3>Mensaje</h3>
        <p>{message.replace("\n", "<br>")}</p>
        </body>
    </html>
    """
    msg.add_alternative(html, subtype="html")
    msg["Subject"] = "Nuevo mensaje de contacto"
    msg["From"] = settings.SMTP_USER
    msg["To"] = "jackson.omegatech@gmail.com"

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
        smtp.login(settings.SMTP_USER, settings.SMTP_PASS)
        smtp.send_message(msg)

@app.post("/contact")
async def send_contact(background_tasks: BackgroundTasks,
                       subject: str = Form(...),
                       name: str = Form(...),
                       email: EmailStr = Form(...),
                       message: str = Form(...)):

    background_tasks.add_task(send_email_sync, subject, name, email, message)
    return {"status": "queued"}