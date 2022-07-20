from pydantic import BaseModel
from typing import Union


class Article(BaseModel):
    url: str
    article_id: str
    meta_data: dict


class ArticleTask(BaseModel):
    url: str
    article_id: Union[str, None] = None
    # kwargs为http请求参数, 包括headers, proxy, body, method...
    http_kwargs: Union[dict, None] = None
    property: Union[int, None] = 0
