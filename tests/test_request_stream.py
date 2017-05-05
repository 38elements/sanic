from sanic import Sanic
from sanic.blueprints import Blueprint
from sanic.response import stream, text

bp = Blueprint('test_blueprint_request_stream')
app = Sanic('test_request_stream', is_request_stream=True)


@app.stream('/stream')
async def handler(request):
    async def streaming(response):
        while True:
            body = await request.stream.get()
            if body is None:
                break
            body = body.decode('utf-8').replace('1', 'A')
            response.write(body)
    return stream(streaming)


@app.get('/get')
async def get(request):
    return text('OK')


@bp.stream('/bp_stream')
async def bp_handler(request):
    result = ''
    while True:
        body = await request.stream.get()
        if body is None:
            break
        result += body.decode('utf-8').replace('1', 'A')
    return text(result)

app.blueprint(bp)


def test_request_stream():
    data = ""
    for i in range(1, 250000):
        data += str(i)
    request, response = app.test_client.post('/stream', data=data)
    text = data.replace('1', 'A')
    assert response.status == 200
    assert response.text == text

    request, response = app.test_client.get('/get')
    assert response.status == 200
    assert response.text == 'OK'

    request, response = app.test_client.post('/bp_stream', data=data)
    assert response.status == 200
    assert response.text == text
