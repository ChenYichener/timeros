"""
邮件客户端模块。

提供邮件发送功能，用于任务执行结果的通知。
支持SMTP协议发送邮件。
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional

from app.utils.exceptions import TaskExecutionError
from app.utils.logger import get_logger
from config.settings import settings

logger = get_logger(__name__)


class EmailClient:
    """
    邮件客户端类。

    封装邮件发送功能，支持发送文本和HTML格式的邮件。
    用于任务执行结果的通知。
    """

    def __init__(
        self,
        smtp_host: Optional[str] = None,
        smtp_port: int = 587,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
    ):
        """
        初始化邮件客户端。

        Args:
            smtp_host: SMTP服务器地址
            smtp_port: SMTP服务器端口
            smtp_user: SMTP用户名（通常是邮箱地址）
            smtp_password: SMTP密码
        """
        self.smtp_host = smtp_host or settings.SMTP_HOST
        self.smtp_port = smtp_port or settings.SMTP_PORT
        self.smtp_user = smtp_user or settings.SMTP_USER
        self.smtp_password = smtp_password or settings.SMTP_PASSWORD

    def send_email(
        self,
        to_addresses: List[str],
        subject: str,
        body: str,
        is_html: bool = False,
        from_address: Optional[str] = None,
    ) -> bool:
        """
        发送邮件。

        Args:
            to_addresses: 收件人地址列表
            subject: 邮件主题
            body: 邮件正文
            is_html: 是否为HTML格式
            from_address: 发件人地址，如果为None则使用配置中的地址

        Returns:
            True表示发送成功，False表示发送失败

        Raises:
            TaskExecutionError: 当邮件配置不完整或发送失败时
        """
        if not all([self.smtp_host, self.smtp_user, self.smtp_password]):
            error_msg = "邮件配置不完整，无法发送邮件"
            logger.error(error_msg)
            raise TaskExecutionError(error_msg)

        try:
            from_address = from_address or self.smtp_user

            # 创建邮件消息
            msg = MIMEMultipart("alternative")
            msg["From"] = from_address
            msg["To"] = ", ".join(to_addresses)
            msg["Subject"] = subject

            # 添加邮件正文
            if is_html:
                msg.attach(MIMEText(body, "html", "utf-8"))
            else:
                msg.attach(MIMEText(body, "plain", "utf-8"))

            # 连接SMTP服务器并发送
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg, from_address, to_addresses)

            logger.info(
                f"邮件发送成功: to={to_addresses}, subject={subject}",
                extra={"to": to_addresses},
            )
            return True

        except Exception as e:
            error_msg = f"发送邮件失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise TaskExecutionError(error_msg) from e

    def send_task_result(
        self,
        to_addresses: List[str],
        task_name: str,
        result: str,
        is_success: bool = True,
    ) -> bool:
        """
        发送任务执行结果邮件。

        格式化任务执行结果并发送邮件通知。

        Args:
            to_addresses: 收件人地址列表
            task_name: 任务名称
            result: 任务执行结果
            is_success: 是否执行成功

        Returns:
            True表示发送成功
        """
        status = "成功" if is_success else "失败"
        subject = f"任务执行{status}: {task_name}"

        # 构建HTML格式的邮件正文
        body = f"""
        <html>
        <body>
            <h2>任务执行{status}</h2>
            <p><strong>任务名称:</strong> {task_name}</p>
            <p><strong>执行状态:</strong> {status}</p>
            <h3>执行结果:</h3>
            <pre>{result}</pre>
        </body>
        </html>
        """

        return self.send_email(
            to_addresses=to_addresses,
            subject=subject,
            body=body,
            is_html=True,
        )

