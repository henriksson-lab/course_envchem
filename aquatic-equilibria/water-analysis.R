# Activity A. Constructed near-neutral water analyses, not environmental samples.
# Run from the folder holding this script and the two CSVs. Raw data are retained.
library(readr)
library(dplyr)
library(ggplot2)

raw_ions <- read_csv("water-ions.csv", show_col_types = FALSE)
corrections <- read_csv("corrections.csv", show_col_types = FALSE)
stopifnot(!anyNA(raw_ions),
          all(raw_ions$concentration_mg_l >= 0),
          all(raw_ions$molar_mass_g_mol > 0),
          all(raw_ions$charge != 0),
          anyDuplicated(raw_ions[c("sample_id", "ion")]) == 0)

# mg/L divided by the numerical g/mol value gives mmol/L.
raw_calculated <- raw_ions |>
  mutate(concentration_mmol_l = concentration_mg_l / molar_mass_g_mol,
         positive_meq_l = if_else(charge > 0,
                                  charge * concentration_mmol_l, 0),
         negative_meq_l = if_else(charge < 0,
                                  -charge * concentration_mmol_l, 0))
raw_balance <- raw_calculated |>
  group_by(sample_id) |>
  summarise(cations_meq_l = sum(positive_meq_l),
            anions_meq_l = sum(negative_meq_l), .groups = "drop") |>
  mutate(imbalance_percent =
           100 * (cations_meq_l - anions_meq_l) /
                 (cations_meq_l + anions_meq_l))

# Apply ONLY the supplied correction supported by the constructed lab record.
# A charge mismatch by itself is not authority to invent a replacement value.
stopifnot(nrow(corrections) == 1)
corrected_ions <- raw_ions
row_to_correct <- which(raw_ions$sample_id == corrections$sample_id[1] &
                        raw_ions$ion == corrections$ion[1])
stopifnot(length(row_to_correct) == 1,
          abs(raw_ions$concentration_mg_l[row_to_correct] -
                corrections$original_mg_l[1]) < 1e-8)
corrected_ions$concentration_mg_l[row_to_correct] <-
  corrections$corrected_mg_l[1]

corrected_calculated <- corrected_ions |>
  mutate(concentration_mmol_l = concentration_mg_l / molar_mass_g_mol,
         positive_meq_l = if_else(charge > 0,
                                  charge * concentration_mmol_l, 0),
         negative_meq_l = if_else(charge < 0,
                                  -charge * concentration_mmol_l, 0))
corrected_balance <- corrected_calculated |>
  group_by(sample_id) |>
  summarise(cations_meq_l = sum(positive_meq_l),
            anions_meq_l = sum(negative_meq_l), .groups = "drop") |>
  mutate(imbalance_percent =
           100 * (cations_meq_l - anions_meq_l) /
                 (cations_meq_l + anions_meq_l))

water_plot <- ggplot(corrected_calculated,
                     aes(ion, concentration_mmol_l, colour = sample_id,
                         shape = sample_id)) +
  geom_point(position = position_dodge(width = 0.45), size = 2.8) +
  labs(x = "Ion", y = "Concentration (mmol/L)", colour = "Sample", shape = "Sample",
       subtitle = "Constructed water data after the documented correction") +
  theme_minimal(base_size = 13) +
  theme(legend.position = "bottom")
