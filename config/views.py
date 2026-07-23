from django.shortcuts import render
from django.http import HttpResponse

def handler404(request, exception):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)

def robots_txt(request):
    content = """User-agent: *
Allow: /
Disallow: /admin-site-panel-dashboard-panel-60d731db-admin/
Disallow: /api/

Sitemap: https://www.ithouse.academy/sitemap.xml
"""
    return HttpResponse(content, content_type='text/plain')

def sitemap_xml(request):
    content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://www.ithouse.academy/</loc>
    <lastmod>2026-07-23</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://www.ithouse.academy/login/</loc>
    <lastmod>2026-07-23</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
</urlset>
"""
    return HttpResponse(content, content_type='application/xml')