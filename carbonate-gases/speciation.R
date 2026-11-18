# Carbonate distribution at supplied pH, dilute freshwater, 25 degrees C.
# Constructed model predictions, not measured data. Run from this file's folder.
# No pH solver: pH is the independent input at every row.
library(ggplot2)

pH <- seq(4, 12, by = 0.05)
r1 <- 10^(pH - 6.35)
r2 <- 10^(pH - 10.33)
denominator <- 1 + r1 + r1 * r2
speciation <- data.frame(
  pH = pH,
  alpha_CO2 = 1 / denominator,
  alpha_HCO3 = r1 / denominator,
  alpha_CO3 = r1 * r2 / denominator
)

# One row per pH and species makes a familiar table for ggplot.
plot_data <- data.frame(
  pH = rep(speciation$pH, times = 3),
  fraction = c(speciation$alpha_CO2, speciation$alpha_HCO3,
               speciation$alpha_CO3),
  species = factor(rep(c("CO2*", "HCO3-", "CO3^2-"),
                       each = nrow(speciation)),
                   levels = c("CO2*", "HCO3-", "CO3^2-"))
)

speciation_plot <- ggplot(plot_data, aes(pH, fraction, colour = species,
                                        linetype = species)) +
  geom_line(linewidth = 0.9) +
  geom_vline(xintercept = c(6.35, 10.33), linetype = "dotted",
             colour = "grey50") +
  scale_colour_manual(values = c("#2468A0", "#25713E", "#AD4825")) +
  scale_y_continuous(limits = c(0, 1), breaks = seq(0, 1, 0.25)) +
  labs(x = "Prescribed pH", y = "Fraction of dissolved inorganic carbon",
       colour = "Species", linetype = "Species",
       subtitle = "Dilute freshwater model, 25 °C; dotted lines mark pKa values") +
  theme_minimal(base_size = 13) +
  theme(legend.position = "bottom")
