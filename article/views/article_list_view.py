from rest_framework.views import APIView
from django.db import transaction
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.response import Response
from rest_framework.exceptions import (
    NotAuthenticated,
    ParseError,
)
from article.models import Hashtag, Article
from article.serializers import ArticleDetailSerializer, ArticleListSerializer


class ArticlesView(APIView):
    """게시글 리스트 뷰"""

    serializer_class = ArticleListSerializer

    def get(self, request):
        filtered = Article.objects.all()
        print(filtered)
        query_params = request.query_params

        if "hashtag" in query_params:
            filtered = filtered.filter(hashtag__name__exact=query_params["hashtag"])
        else:
            if request.user.is_authenticated:
                filtered = filtered.filter(hashtag__name__exact=request.user.account)
        if "type" in query_params:
            filtered = filtered.filter(type__exact=query_params["type"])

        search_by = query_params.get("search_by", "title,content")
        if "search" in query_params:
            if search_by == "title":
                # 제목에서만 검색
                filtered = filtered.filter(title__icontains=query_params["search"])
            elif search_by == "content":
                # 내용에서만 검색
                filtered = filtered.filter(content__icontains=query_params["search"])
            else:
                # 제목과 내용에서 검색
                search_result = filtered.filter(title__icontains=query_params["search"])
                cotent_result = filtered.filter(
                    content__icontains=query_params["search"]
                )
                filtered = search_result.union(cotent_result)
        order_filed = query_params.get("order_by", "created_at")
        valid_order_by = [
            "created_at",
            "updated_at",
            "like_cnt",
            "share_cnt",
            "view_cnt",
            "-created_at",
            "-updated_at",
            "-like_cnt",
            "-share_cnt",
            "-view_cnt",
        ]
        if order_filed in valid_order_by:
            filtered = filtered.order_by(order_filed)

        page = int(query_params.get("page", 1))
        page_count = int(query_params.get("page_count", 3))
        start = (page - 1) * page_count
        end = start + page_count

        serializer = ArticleListSerializer(
            filtered[start:end],
            many=True,
        )

        return Response(serializer.data)

    def post(self, request):
        if request.user.is_authenticated:
            # 로그인한 유저인지
            serializer = ArticleDetailSerializer(data=request.data)
            if serializer.is_valid():
                # 모델에 유효한 값인지
                article = serializer.save(user=request.user)
                # 작성자가 누구인지 같이 저장한다
                tags = request.data["hashtag"]
                # 사용자가 등록하려고한 태그 스트링 뭉치
                for word in tags.split():
                    if word.startswith("#"):
                        hashtag_obj, created = Hashtag.objects.get_or_create(
                            name=word[1:]
                        )
                        # 각 단어가 해쉬태그엔티티에 존재하면 그 객체를 보내주고 아니면 생성
                        article.hashtag.add(hashtag_obj.pk)
                serializer = ArticleDetailSerializer(article)
                return Response(serializer.data)
            else:
                return Response(serializer.errors)
        else:
            raise NotAuthenticated
