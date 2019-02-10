air and dirt give oxygen and nutrients to all plants nearby

spaces that are not plant that accumulate energy >= GROW_THRESHOLD become plants. Their nutrients and oxygen levels are set to 0

plants with energy > GROW_THRESHOLD + 8*2 can give 2 energy to all surrounding spaces.
plants with no energy die and turn into empty
plants with both OXYGEN_FOR_ENERGY oxygen and NUTRIENTS_FOR_ENERGY nutrients can remove both to produce ENERGY_FROM_PHOTO energy
plants lose ENERGY_DECAY per turn
