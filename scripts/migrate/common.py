"""Shared header/footer HTML for the site.

HEADER/FOOTER are calibrated for pages one level below site root (currently
just articles/index.html, the archive listing). HEADER_ROOT/FOOTER_ROOT are
for individual article pages, which live at site root with clean slug URLs
(e.g. /cottagecore-bedroom-ideas-worth-trying), with the archive listing
still reachable at /articles/.
"""

HEADER = """<header class="site-header">
    <div class="container header-inner">
      <a href="../index.html" class="logo">Sarah&nbsp;Shahroz</a>

      <nav class="main-nav" id="main-nav">
        <a href="../index.html#latest">Latest</a>
        <a href="index.html">All Articles</a>
        <a href="../index.html#categories">Categories</a>
        <a href="../index.html#about">About</a>
        <a href="../index.html#newsletter">Newsletter</a>
      </nav>

      <button class="nav-toggle" id="nav-toggle" aria-label="Toggle menu">
        <span></span><span></span><span></span>
      </button>
    </div>
  </header>
"""

FOOTER = """<footer class="site-footer">
    <div class="container footer-inner">
      <p>&copy; 2026 Sarah Shahroz. All rights reserved.</p>
      <div class="footer-links">
        <a href="#">Instagram</a>
        <a href="#">Pinterest</a>
        <a href="#">Contact</a>
      </div>
    </div>
  </footer>

  <script src="../js/script.js"></script>
"""

HEADER_ROOT = """<header class="site-header">
    <div class="container header-inner">
      <a href="index.html" class="logo">Sarah&nbsp;Shahroz</a>

      <nav class="main-nav" id="main-nav">
        <a href="index.html#latest">Latest</a>
        <a href="articles/index.html">All Articles</a>
        <a href="index.html#categories">Categories</a>
        <a href="index.html#about">About</a>
        <a href="index.html#newsletter">Newsletter</a>
      </nav>

      <button class="nav-toggle" id="nav-toggle" aria-label="Toggle menu">
        <span></span><span></span><span></span>
      </button>
    </div>
  </header>
"""

FOOTER_ROOT = """<footer class="site-footer">
    <div class="container footer-inner">
      <p>&copy; 2026 Sarah Shahroz. All rights reserved.</p>
      <div class="footer-links">
        <a href="#">Instagram</a>
        <a href="#">Pinterest</a>
        <a href="#">Contact</a>
      </div>
    </div>
  </footer>

  <script src="js/script.js"></script>
"""

NEWSLETTER_SECTION = """<section class="newsletter" id="newsletter">
      <div class="container newsletter-inner">
        <h2>Get new posts in your inbox</h2>
        <p>One email a week. No spam, no sponsored clutter &mdash; just the latest stories.</p>
        <form class="newsletter-form">
          <input type="email" placeholder="Your email address" aria-label="Email address" required>
          <button type="submit" class="btn btn-primary">Subscribe</button>
        </form>
      </div>
    </section>
"""
