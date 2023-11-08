import React from 'react';
import { abbreviate, getPluriel } from '../utils';
import { useApi } from '../hooks';
import { Profession } from '../types';


function getLabel(profession: Profession, feminin: boolean, pluriel: boolean) {
  if (feminin) {
    const nomFeminin = profession.nom_feminin || profession.nom;
    if (pluriel) {
      return profession.nom_feminin_pluriel || getPluriel(nomFeminin);
    }
    return nomFeminin;
  }
  if (pluriel) {
    return profession.nom_pluriel || getPluriel(profession.nom);
  }
  return profession.nom;
}


export default function ProfessionLabel({id, feminin, pluriel}: {id: number; feminin: boolean; pluriel: boolean}) {
  const { data: profession } = useApi<Profession>("professions", id);

  if (!profession) {
    return null;
  }

  return (
    <a href={profession.front_url}>
      {abbreviate(getLabel(profession, feminin, pluriel), 3)}
    </a>
  );
}
