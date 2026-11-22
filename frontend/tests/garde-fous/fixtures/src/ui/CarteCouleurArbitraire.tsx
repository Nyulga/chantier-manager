// Violation volontaire : des valeurs Tailwind arbitraires (couleur, taille, variante) en dur,
// dans une chaîne simple et dans un gabarit de texte.
export function CarteCouleurArbitraire({ etat }: { readonly etat: string }) {
  return (
    <div className="bg-[#F2A900] md:p-[13px] [&_p]:mt-2">
      <p className={`text-[14px] ${etat}`}>{etat}</p>
    </div>
  );
}
