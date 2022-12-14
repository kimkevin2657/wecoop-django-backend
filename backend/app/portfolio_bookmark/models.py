from app.common.models import BaseModel
from django.db import models


class PortfolioBookmark(BaseModel):
    user = models.ForeignKey(
        "user.User", related_name="bookmark_portfolio_users", verbose_name="포트폴리오 찜한 유저", on_delete=models.CASCADE
    )
    portfolio = models.ForeignKey(
        "portfolio.Portfolio", related_name="bookmark_portfolios", verbose_name="찜한 포트폴리오", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "포트폴리오 찜"
        verbose_name_plural = verbose_name
        ordering = ["-created"]

    def __str__(self):
        return f"{self.portfolio}"
