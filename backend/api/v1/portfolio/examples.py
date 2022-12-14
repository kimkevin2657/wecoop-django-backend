from drf_spectacular.utils import OpenApiExample


success = OpenApiExample(
    name="포트폴리오 생성 요청",
    description="포트폴리오 생성 요청 예시입니다.",
    request_only=True,
    value={
        "title": "포트폴리오 제목1",
        "category": "디자인 & 그래픽",
        "mainImage": "image form",
        "images": ["image1 form", "image2 form"],
        "videoUrl": "https://www.video-url.com",
        "workStartYear": 2022,
        "workStartMonth": 8,
        "workEndYear": 2022,
        "workEndMonth": 12,
    },
)
portfolio_create_examples = [success]
