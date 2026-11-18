# Activity C. Fictitious neutral compounds and stipulated process constants.
# Both phases transform parent at the same k; partitioning is rapid and constant.
library(readr)
library(dplyr)
library(ggplot2)

compounds <- read_csv("compounds.csv", show_col_types = FALSE)
stopifnot(!anyNA(compounds), anyDuplicated(compounds$compound_id) == 0,
          all(compounds$kd_l_kg >= 0), all(compounds$half_life_days > 0),
          all(compounds$initial_parent_mg >= 0),
          all(compounds$water_volume_l > 0), all(compounds$dry_solid_kg >= 0))
# rep repeats the supplied inputs across time; no parameter fitting is performed.
fate <- compounds[rep(seq_len(nrow(compounds)), each = 61), ]
fate$time_days <- rep(seq(0, 60, by = 1), times = nrow(compounds))
fate <- fate |>
  mutate(k_per_day = log(2) / half_life_days,
         remaining_fraction = exp(-k_per_day * time_days),
         total_parent_mg = initial_parent_mg * remaining_fraction,
         water_mg_l = total_parent_mg /
           (water_volume_l + kd_l_kg * dry_solid_kg),
         water_parent_mg = water_mg_l * water_volume_l,
         solid_mg_kg = kd_l_kg * water_mg_l,
         solid_parent_mg = solid_mg_kg * dry_solid_kg,
         transformed_parent_mg = initial_parent_mg - total_parent_mg)

fate_plot <- ggplot(fate, aes(time_days, water_mg_l,
                             colour = compound_id, linetype = compound_id)) +
  geom_line(linewidth = 0.9) +
  labs(x = "Time (days)", y = "Water-phase parent concentration (mg/L)",
       colour = "Fictitious compound", linetype = "Fictitious compound",
       subtitle = "Closed, rapidly equilibrating two-phase teaching model") +
  theme_minimal(base_size = 13) +
  theme(legend.position = "bottom")
