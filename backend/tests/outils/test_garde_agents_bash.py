"""Garde des sous-agents : commandes git interdites et commandes d'écriture des vérificateurs."""

import pytest

from tests.outils.appels_garde_agents import RACINE, commande
from tools.garde_agents import decider

VERIFICATEURS = ("revue", "conformite", "securite")


@pytest.mark.parametrize(
    "texte",
    [
        "git commit -m x",
        "git push",
        "git push origin dev",
        "git checkout dev",
        "git reset --hard",
        "git stash",
        "git switch main",
        "git restore f",
        "git rebase main",
        "git merge dev",
        "git clean -fd",
        "git -C backend push",
        "git -c user.name=x commit",
        "git --git-dir=.git --no-pager commit",
        "git --git-dir .git --work-tree . reset",
        "cd a && git reset --hard",
        'bash -c "git stash"',
        "sh -lc 'echo ok; git push'",
        "/usr/bin/git checkout dev",
        "git.exe commit -m x",
        "X=1 git rebase main",
        "echo ok; git clean -fd",
        "echo ok | git commit -F -",
        "echo $(git push)",
        "echo `git push`",
        "(git push)",
        "false || git push",
        "sleep 1 &\ngit push",
        "if true; then git commit -m x; fi",
        "env GIT_DIR=. git push",
        'echo "a;b"; git commit',
        'echo "ouvert; git commit',
        "git push \\",
        'bash --norc -c "git push"',
    ],
)
def test_une_commande_git_qui_modifie_le_depot_est_refusee_aux_sous_agents(texte: str) -> None:
    raison = decider(commande("dev-api", texte), RACINE)

    assert raison is not None
    assert "git" in raison
    assert "coordinateur" in raison


@pytest.mark.parametrize(
    "texte",
    [
        "git status",
        "git diff --stat",
        "git log --oneline -3",
        "git -C backend status",
        "git",
        "git -c",
        "just verifier",
        'grep -n "git push" docs/x.md',
        "echo commit",
        "echo 'git push; git commit'",
        "ls -la",
        "",
        "   ",
        "bash script.sh",
        "bash -c",
    ],
)
def test_les_commandes_sans_risque_sont_acceptees(texte: str) -> None:
    assert decider(commande("dev-api", texte), RACINE) is None


def test_une_commande_ecriture_sans_effet_sur_le_depot_est_acceptee_pour_les_ecrivains() -> None:
    assert decider(commande("dev-socle", "rm -rf node_modules"), RACINE) is None


@pytest.mark.parametrize("agent", VERIFICATEURS)
@pytest.mark.parametrize(
    "texte",
    [
        "rm -rf x",
        "mv a b",
        "cp a b",
        "sed -i s/a/b/ f",
        "sed -ni s/a/b/p f",
        "sed -i.bak s/a/b/ f",
        "sed --in-place s/a/b/ f",
        "cat a | tee b",
        "echo ok && rm f",
        "/bin/rm f",
        'bash -c "rm f"',
    ],
)
def test_les_verificateurs_ne_peuvent_pas_ecrire_par_commande(agent: str, texte: str) -> None:
    raison = decider(commande(agent, texte), RACINE)

    assert raison is not None
    assert "coordinateur" in raison


@pytest.mark.parametrize("agent", VERIFICATEURS)
@pytest.mark.parametrize(
    "texte",
    [
        "sed -n 1,5p f",
        "sed -e s/a/b/ f",
        "sed --silent 1p f",
        "just verifier",
        "git diff",
        'grep -rn "rm -rf" docs',
        "ls rm",
    ],
)
def test_les_verificateurs_peuvent_lire(agent: str, texte: str) -> None:
    assert decider(commande(agent, texte), RACINE) is None


@pytest.mark.parametrize("agent", ["pentest", "backlog"])
def test_pentest_et_backlog_ne_sont_limites_que_par_la_garde_git(agent: str) -> None:
    assert decider(commande(agent, "tee rapport.md"), RACINE) is None
    assert decider(commande(agent, "git push"), RACINE) is not None
