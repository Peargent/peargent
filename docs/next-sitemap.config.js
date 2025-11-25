/** @type {import('next-sitemap').IConfig} */
module.exports = {
  siteUrl: process.env.SITE_URL || 'https://peargent.online',
  generateRobotsTxt: true,
  generateIndexSitemap: false, // Generate a single sitemap.xml instead of index + sitemap-0.xml
  sitemapSize: 7000,
}
