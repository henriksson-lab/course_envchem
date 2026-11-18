# Course-level chemistry and student-workflow verification. Run from repo root.
# Examples are constructed; checks verify their stated models, not field accuracy.
near <- function(actual, expected, tol=1e-8) {
  stopifnot(all(is.finite(actual)), max(abs(actual-expected)) < tol)
}
# Unit conversions, mixing, and loads.
near((2*3+1*.6)/3,2.2)
near((4*2)/5,1.6)
near(.2*1000*.5/1e6*86400,8.64)
near(10*2,20); near(40*1,40)
# Atmospheric one-sink examples and annual deposition budget.
near(1/(1e-12*1e6)/86400,11.574074074,1e-8)
near(.6*1000*20e-6,.012)
near((.02+2*.01)*1e6,40000)
near((40000-30000)/5e8*1000,.02)
near((50000-10000)/5e8*1000,.08)
near((50000-20000)/5e8*1000,.06)
near(log(2)/.02,34.65735903,1e-7)
near(exp(-.02*50),.367879441,1e-8)
# Acid distribution, ionic strength, binding, and saturation.
near(.2*10/11,.1818181818,1e-8)
near(.5*(.001*4+.002),.003)
near(2/(1+1e6*1e-5),.1818181818,1e-8)
near(1e-16/(1e-5)^2,1e-6)
# Sorption, oxygen, treatment, exchange, and neutralisation inventories.
near(1/(1+100*.01),.5)
near(1/(1+100*.02),1/3)
near(1/(1+10*.01),10/11)
near(3*32/12,8)
near(9-2*32/12,11/3)
near(.08*5/4*12,1.2)
near(100*.7*.7,49)
near(10*.01*.2*.5/2,.005)
near(.01*4-.015*2,.01)
near(.02*5000,100)
near(1/(1+10^(6.5-4.5)),1/101)
# Independently balance named reactions. Rows are element counts and charge;
# signed stoichiometric coefficients are negative for reactants.
check_reaction <- function(composition, coefficients) {
  stopifnot(max(abs(composition %*% coefficients)) < 1e-12)
}
# Cl+O3 -> ClO+O2; ClO+O -> Cl+O2.
check_reaction(rbind(Cl=c(1,0,1,0), O=c(0,3,1,2)),c(-1,-1,1,1))
check_reaction(rbind(Cl=c(1,0,1,0), O=c(1,1,0,2)),c(-1,-1,1,1))
# Nitrification: NH4+, O2, NO3-, H+, H2O.
check_reaction(rbind(N=c(1,0,1,0,0), H=c(4,0,0,1,2),
                     O=c(0,2,3,0,1), charge=c(1,0,-1,1,0)),
               c(-1,-2,1,2,1))
# Denitrification: NO3-, CH2O, H+, N2, CO2, H2O.
check_reaction(rbind(N=c(1,0,0,2,0,0), C=c(0,1,0,0,1,0),
                     H=c(0,2,1,0,0,2), O=c(3,1,0,0,2,1),
                     charge=c(-1,0,1,0,0,0)),c(-4,-5,-4,2,5,7))
# Iron half-reaction: FeOOH, H+, e-, Fe2+, H2O.
check_reaction(rbind(Fe=c(1,0,0,1,0), O=c(2,0,0,0,1),
                     H=c(1,1,0,0,2), charge=c(0,1,-1,2,0)),
               c(-1,-3,-1,1,2))
# Sulfate half-reaction: SO4--, H+, e-, HS-, H2O.
check_reaction(rbind(S=c(1,0,0,1,0), O=c(4,0,0,0,1),
                     H=c(0,1,0,1,2), charge=c(-2,1,-1,-1,0)),
               c(-1,-9,-8,1,4))
# Combined pyrite oxidation: FeS2, O2, H2O, Fe(OH)3, SO4--, H+.
check_reaction(rbind(Fe=c(1,0,0,1,0,0), S=c(2,0,0,0,1,0),
                     O=c(0,2,1,3,4,0), H=c(0,0,2,3,0,1),
                     charge=c(0,0,0,0,-2,1)),c(-1,-15/4,-7/2,1,2,4))

# Run supplied scripts in isolated environments for direct model checks.
water <- new.env()
old <- setwd('aquatic-equilibria')
sys.source('water-analysis.R',envir=water)
setwd(old)
near(water$raw_balance$imbalance_percent,c(0,0,100*.36/3.64))
near(water$corrected_balance$imbalance_percent,c(0,0,0))
stopifnot(identical(water$raw_ions$concentration_mg_l,
                    readr::read_csv('aquatic-equilibria/water-ions.csv',
                                   show_col_types=FALSE)$concentration_mg_l))
ggplot2::ggsave('aquatic-equilibria/water-ions.svg',water$water_plot,
                width=8.4,height=4.6,device=grDevices::svg,bg='white')

fate_model <- new.env()
old <- setwd('organic-contaminants')
sys.source('fate.R',envir=fate_model)
setwd(old)
f <- fate_model$fate
near(f$water_parent_mg+f$solid_parent_mg,f$total_parent_mg)
near(f$total_parent_mg+f$transformed_parent_mg,f$initial_parent_mg)
stopifnot(all(f$remaining_fraction>=0),all(f$remaining_fraction<=1))
near(f$remaining_fraction[f$time_days==0],c(1,1))
near(f$remaining_fraction[f$time_days==f$half_life_days],c(.5,.5))
near(f$water_mg_l[f$compound_id=='U' & f$time_days==20],.125)
near(f$water_mg_l[f$compound_id=='V' & f$time_days==30],.5/1.1)
ggplot2::ggsave('organic-contaminants/fate.svg',fate_model$fate_plot,
                width=8.4,height=4.6,device=grDevices::svg,bg='white')

# Reference plots from the stated analytical models; no fitted data.
library(ggplot2)
ligand <- data.frame(free_ligand_mol_l=10^seq(-9,-3,length.out=151))
ligand$free_metal_fraction <- 1/(1+1e6*ligand$free_ligand_mol_l)
p <- ggplot(ligand,aes(free_ligand_mol_l,free_metal_fraction))+
  geom_line(linewidth=.9,colour='#2468A0')+scale_x_log10()+
  labs(x='Prescribed free ligand (mol/L)',y='Fraction of metal remaining free',
       subtitle='One-complex teaching model; beta = 10^6 L/mol')+
  theme_minimal(base_size=13)
ggsave('metals/binding.svg',p,width=8,height=4.2,device=grDevices::svg,bg='white')
sorb <- data.frame(dry_solid_kg=seq(0,.05,length.out=151))
sorb$water_mg_l <- 1/(1+100*sorb$dry_solid_kg)
p <- ggplot(sorb,aes(dry_solid_kg,water_mg_l))+
  geom_line(linewidth=.9,colour='#25713E')+
  labs(x='Dry solid mass (kg)',y='Equilibrium water concentration (mg/L)',
       subtitle='Closed bottle: 1 mg total, 1 L water, Kd = 100 L/kg')+
  theme_minimal(base_size=13)
ggsave('surfaces/partition.svg',p,width=8,height=4.2,device=grDevices::svg,bg='white')

# Render the other two reports from portable copies in fresh R subprocesses.
render_portable <- function(folder,files,report) {
  temp <- tempfile('envchem-student-');dir.create(temp)
  stopifnot(all(file.copy(file.path(folder,files),temp)))
  prior <- setwd(temp)
  expr <- sprintf('rmarkdown::render(%s, quiet=TRUE)',dQuote(report,FALSE))
  status <- system2(file.path(R.home('bin'),'Rscript'),
                    c('--vanilla','-e',shQuote(expr)))
  setwd(prior)
  stopifnot(status==0,file.exists(file.path(temp,sub('Rmd$','html',report))))
}
render_portable('aquatic-equilibria',
                c('water-ions.csv','corrections.csv','water-analysis.R','water-report.Rmd'),
                'water-report.Rmd')
render_portable('organic-contaminants',
                c('compounds.csv','fate.R','fate-report.Rmd'),'fate-report.Rmd')
cat('Course numeric, atom/charge balance, two-phase, data-quality, and portable-report checks passed.\n')
