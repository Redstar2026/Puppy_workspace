import urllib.request, ssl, os

os.makedirs('bq_results', exist_ok=True)

proxy  = urllib.request.ProxyHandler({'http':'http://sysproxy.wal-mart.com:8080','https':'http://sysproxy.wal-mart.com:8080'})
ctx    = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode    = ssl.CERT_NONE
opener = urllib.request.build_opener(proxy, urllib.request.HTTPSHandler(context=ctx))
req    = urllib.request.Request(
    'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js',
    headers={'User-Agent': 'Mozilla/5.0'}
)
with opener.open(req, timeout=30) as r:
    data = r.read()
with open('chartjs.min.js', 'wb') as f:
    f.write(data)
print(f'Chart.js descargado: {len(data):,} bytes')
