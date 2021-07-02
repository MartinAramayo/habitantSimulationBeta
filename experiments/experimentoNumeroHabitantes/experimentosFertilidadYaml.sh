a=(10 \
 500 \
 1000 \
 1500 \
 2500 \
 3000 \
 3500 \
 4000 \
 4500 \
 5000)

for leadingZero in {01..10}; do 
    # leadingZero tiene leading zero
    fileHere=experimento"$leadingZero".yaml
    rm "$fileHere"
    touch "$fileHere"
    
    index="$(expr $leadingZero - 1)" # indice sin leading zero
    
    value="${a[$index]}" # value en la lista

    echo "n_iteraciones: 2000" >> "$fileHere"
    echo "p_emancipate: 0.3" >> "$fileHere"
    echo "p_partner: 0.3" >> "$fileHere"
    echo "p_child: 0.1" >> "$fileHere"
    echo "p_premature_death: 0.001" >> "$fileHere"
    echo "initial_condition:" >> "$fileHere"
    echo "  num_houses: $value" >> "$fileHere"
    echo "  ratio: 0.5" >> "$fileHere"
    echo "  my_mu:" >> "$fileHere"
    echo "  house_size: 3" >> "$fileHere"
    echo "comment: |" >> "$fileHere"
    echo "  Baja fertilidad y muerte prematura no nula" >> "$fileHere"
done
