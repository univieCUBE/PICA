

phenotypes = ("JGIB_AEROBE","JGIB_ANAEROBE","JGIB_HYPER_THERM","JGIB_HYPER_THERM_TOLERANT","JGIB_PSYCHRO_TOLERANT","JGIB_HALO","JGIB_FACULTATIVE","JGIB_GRAMNEGATIVE","JGIB_MOTILITY","JGIB_PHOTO","JGIB_SPORE")
sets = ("genotype_prokaryote.cv1-2.profile","genotype_prokaryote.cv2-2.profile")

all_sh = "launch_all.sh"
fall = open(all_sh,"w")
for phenotype in phenotypes:
	for set in sets:
		output_sh = "%s.%s.cpartimings.sh"%(phenotype,set)
		fout = open(output_sh,"w")
		fout.write("python train.py -a cpar.CPARTrainer -s examples/%s -c examples/phenotype_20100209.profile -t %s -o %s.%s.timing.output\n"%(set,phenotype,phenotype,set))
		fall.write("qsub -cwd -l h_rt=002:00:00 %s\n"%(output_sh))
		fout.close()
fall.close()
