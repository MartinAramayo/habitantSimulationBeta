for filename in experiments/experimentoNumeroHabitantes/*.yaml; do
    
    # Imprime el filename
    echo "$filename"
    
    # Prints filename without the suffix.*, without its extension
    echo "${filename%.*}"

    # $ foo=${string#"$prefix"} #elimina el prefijo
    # $ foo=${string%"$suffix"} #elimina el sufijo
    python main2.py "$filename"
done 
