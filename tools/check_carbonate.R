# Run from the repository root. Verify the teaching chemistry, regenerate the
# shared scientific figure, and render the student report in an isolated folder.
source("carbonate-gases/speciation.R")
fractions <- as.matrix(speciation[, c("alpha_CO2", "alpha_HCO3", "alpha_CO3")])
stopifnot(all(is.finite(fractions)), all(fractions >= 0), all(fractions <= 1),
          max(abs(rowSums(fractions) - 1)) < 1e-12)
row <- which(abs(speciation$pH - 8.35) < 1e-8)
stopifnot(length(row) == 1,
          max(abs(fractions[row, ] - c(.009799394, .9799394, .01026123))) < 1e-7,
          fractions[1, 1] > .99, fractions[nrow(fractions), 3] > .97)
# Independently evaluate the H-based mass-action form rather than the ratio form.
k1 <- 10^-6.35; k2 <- 10^-10.33; kw <- 1e-14
h <- 10^-speciation$pH
d <- h^2 + k1*h + k1*k2
independent <- cbind(h^2/d, k1*h/d, k1*k2/d)
stopifnot(max(abs(independent-fractions)) < 1e-12)
for (ph in c(6.35, 10.33)) {
  hyd <- 10^-ph; den <- hyd^2+k1*hyd+k1*k2
  a <- c(hyd^2,k1*hyd,k1*k2)/den
  pair <- if (ph == 6.35) 1:2 else 2:3
  stopifnot(abs(diff(a[pair])) < 1e-12)
}
alkalinity <- function(ph, ct) {
  hyd <- 10^-ph
  den <- hyd^2+k1*hyd+k1*k2
  ct*(k1*hyd+2*k1*k2)/den+kw/hyd-hyd
}
for (ct in c(.001,.0001)) {
  before <- alkalinity(7.5,ct)
  target <- before-50e-6
  final <- uniroot(function(ph) alkalinity(ph,ct)-target,
                   c(2,12), tol=1e-12)$root
  expected <- if (ct == .001) 7.235116 else 6.251551
  stopifnot(abs(final-expected) < 1e-6,
            abs(alkalinity(final,ct)-target) < 1e-12)
  cat(sprintf("CT %.4g mol/L: initial TA %.8g eq/L; final pH %.6f\n",
              ct,before,final))
}
co2 <- .034*4e-4
stopifnot(abs(co2-13.6e-6) < 1e-15,
          abs(co2*(1+100+100*10^-1.98)*1000-1.387841) < 1e-6,
          abs(5e-4*1e-6/3.3e-9-.15151515) < 1e-8,
          abs(5e-4*1e-5/3.3e-9-1.5151515) < 1e-7)
ggsave("carbonate-gases/speciation.svg", speciation_plot,
       width=8.4, height=4.6, device=grDevices::svg, bg="white")
# Build from downloaded source files in a fresh child R process, without
# instructor objects, absolute source paths, or an existing workspace.
report_dir <- tempfile("envchem-report-")
dir.create(report_dir)
file.copy(c("carbonate-gases/speciation.R", "carbonate-gases/report.Rmd"),
          report_dir)
old <- setwd(report_dir)
status <- system2(file.path(R.home("bin"), "Rscript"),
                  c("--vanilla", "-e",
                    shQuote('rmarkdown::render("report.Rmd", quiet=TRUE)')))
setwd(old)
stopifnot(status == 0, file.exists(file.path(report_dir,"report.html")))
cat("Fraction, mass-action, acid-balance, Henry, saturation, and fresh-report checks passed.\n")
