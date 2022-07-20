import json
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.dependencies.response import resp_200
from app.dependencies.models import Article, ArticleTask
from app.dependencies import str_2_md5
from app.dependencies.crawl import crawl_articles

router = APIRouter()

# list
task_key = 'news_downloader:news_tasks'
# hash
articles_key = 'news_downloader:articles'


@router.post("/article_tasks/", tags=["articles"])
async def push_article(request: Request, article: ArticleTask):
    """
    直接处理请求
    从redis判断任务是否存在, 如果存在, 直接返回html
    """
    article.article_id = str_2_md5(article.url)
    # await request.app.state.redis.lpush(task_key, json.dumps(article.dict()))
    # task_len = await request.app.state.redis.llen(task_key)
    # data={
    #     'article_id': article.article_id,
    #     'content': '任务提交成功, 当前队列任务数: {}, 稍后根据article_id查询'.format(task_len),
    # }
    if await request.app.state.redis.hget(articles_key, article.article_id) is None:
        # 爬取文章
        response_status, response_text = await crawl_articles(article.dict())
        print(response_status, response_text)
        res_data = article.dict().copy()
        res_data['res_status_code'] = response_status
        res_data['res_text'] = response_text
        await request.app.state.redis.hset(articles_key, article.article_id, json.dumps(res_data))
    res_data = json.loads(await request.app.state.redis.hget(articles_key, article.article_id))
    data = {
        'content': '请求成功, 通过show_url预览网页, 通过post请求获取全部信息',
        'show_url': 'http://localhost:8000/articles/{}'.format(article.article_id),
        # 'res_data': res_data,
    }
    return resp_200(data=data)


@router.get("/article_tasks/", tags=["articles"])
async def articles(request: Request):
    """
    查询任务队列
    """
    tasks = await request.app.state.redis.lrange(task_key, 0, 10)
    task_len = await request.app.state.redis.llen(task_key)
    data = {
        'tasks': tasks,
        'content': '当前队列任务数: {}, 可根据article_id查询'.format(task_len),
    }
    return resp_200(data=data)


@router.get("/articles/", tags=["articles"])
async def read_user_me(request: Request):
    aritcle_ids = await request.app.state.redis.hkeys(articles_key)
    return resp_200(data={
        'aritcle_ids': aritcle_ids[:10]
    })


@router.get("/articles/{article_id}", tags=["articles"], response_class=HTMLResponse)
async def article(request: Request, article_id: str):
    """
    GET 请求直接返回html
    """
    article = json.loads(await request.app.state.redis.hget(articles_key, article_id))
    if article:
        return article.get('res_text')
    else:
        return resp_200(data=article, message='任务还未处理, 可能需要等待片刻, 或者在提交任务是增加参数: property="1"')


# @router.get("/articles/{article_id}", tags=["articles"])
@router.post("/articles/", tags=["articles"])
async def article(request: Request, post_data: dict):
    """
    POST 请求返回所有数据
    {
        "article_id": "22e6802c154f3ecc0b4c0972bc8852f5"
    }
    """
    article = json.loads(await request.app.state.redis.hget(articles_key, post_data.get("article_id")))
    if article:
        return resp_200(data=article)
    else:
        return resp_200(data=article, message='任务还未处理, 可能需要等待片刻, 或者在提交任务是增加参数: property="1"')


@router.post("/article_tasks/debug", tags=["articles"])
async def debug_article(request: Request, article: ArticleTask):
    article_id = str_2_md5(article.url)
    data = {
        'article_id': article_id,
        'article_dict': article.dict(),
    }
    return resp_200(data=data)
