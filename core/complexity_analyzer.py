# core/complexity_analyzer.py
import re
from typing import Dict, Union

# Nouvelle structure pour le dictionnaire technique avec variantes
TECH_TERMS = {
    # --- Concepts généraux ---
    "blockchain": {"weight": 1, "aliases": ["block chain"]},
    "distributed ledger": {"weight": 1, "aliases": []},
    "node": {"weight": 1, "aliases": ["nodes"]},
    "peer-to-peer": {"weight": 1, "aliases": ["p2p", "peer to peer"]},
    "consensus": {"weight": 1, "aliases": ["consensus mechanism"]},
    "mining": {"weight": 1, "aliases": ["miner", "miners"]},
    "validator": {"weight": 1, "aliases": ["validators"]},
    "fork": {"weight": 1, "aliases": ["forks"]},
    "hard fork": {"weight": 1, "aliases": ["hardfork", "hard forks"]},
    "soft fork": {"weight": 1, "aliases": ["softfork", "soft forks"]},
    "genesis block": {"weight": 1, "aliases": []},
    "block height": {"weight": 1, "aliases": []},
    "transaction": {"weight": 1, "aliases": ["transactions"]},
    "transaction fee": {"weight": 1, "aliases": ["tx fee", "fees", "network fee", "gas fee", "gas fees"]},
    "utxo": {"weight": 1, "aliases": ["unspent transaction output"]},
    "wallet": {"weight": 1, "aliases": ["wallets"]},
    "private key": {"weight": 1, "aliases": ["private keys"]},
    "public key": {"weight": 1, "aliases": ["public keys"]},
    "address": {"weight": 1, "aliases": ["addresses"]},
    "seed phrase": {"weight": 1, "aliases": ["recovery phrase", "backup phrase"]},
    "peer": {"weight": 1, "aliases": ["peers"]},
    "network latency": {"weight": 1, "aliases": []},
    "propagation": {"weight": 1, "aliases": []},
    "block time": {"weight": 1, "aliases": []},
    "chain reorganization": {"weight": 1, "aliases": ["reorg", "reorgs"]},

    # --- Cryptographie ---
    "hash function": {"weight": 3, "aliases": ["hashing function", "cryptographic hash function"]},
    "sha-256": {"weight": 3, "aliases": ["sha256", "sha 256"]}, # Exemple de variante
    "keccak-256": {"weight": 3, "aliases": ["keccak256", "keccak 256"]},
    "elliptic curve": {"weight": 3, "aliases": ["elliptic curve cryptography", "ecc"]},
    "ecdsa": {"weight": 3, "aliases": ["elliptic curve digital signature algorithm"]},
    "digital signature": {"weight": 3, "aliases": ["digital signatures"]},
    "merkle tree": {"weight": 3, "aliases": ["merkle trees", "hash tree", "hash trees"]},
    "merkle root": {"weight": 3, "aliases": []},
    "zero-knowledge proof": {"weight": 3, "aliases": ["zk proof", "zk-proof", "zero knowledge proof", "zkp", "zk-snark", "zk-stark"]},
    # Ajoutons spécifiquement les termes du Bitcoin Whitepaper
    "proof-of-work": {"weight": 3, "aliases": ["pow", "proof of work"]},
    "hashcash": {"weight": 3, "aliases": []},
    "timestamp server": {"weight": 2, "aliases": ["timestamping service"]},
    "double-spending": {"weight": 2, "aliases": ["double spending"]},
    "cpu power": {"weight": 2, "aliases": []}, # Terme spécifique à Bitcoin

    # --- Tokens et économie ---
    "token": {"weight": 1, "aliases": ["tokens"]},
    "cryptocurrency": {"weight": 1, "aliases": ["crypto currency", "crypto currencies"]},
    "stablecoin": {"weight": 1, "aliases": ["stable coin", "stable coins"]},
    "fiat-backed": {"weight": 1, "aliases": []},
    "governance token": {"weight": 1, "aliases": []},
    "utility token": {"weight": 1, "aliases": []},
    "security token": {"weight": 1, "aliases": []},
    "erc-20": {"weight": 1, "aliases": ["erc20"]},
    "erc-721": {"weight": 1, "aliases": ["erc721"]},
    "erc-1155": {"weight": 1, "aliases": ["erc1155"]},
    "minting": {"weight": 1, "aliases": ["mint"]},
    "burning": {"weight": 1, "aliases": ["burn"]},
    "supply cap": {"weight": 1, "aliases": []},
    "inflation rate": {"weight": 1, "aliases": []},
    "deflationary token": {"weight": 1, "aliases": []},
    "airdrop": {"weight": 1, "aliases": ["air drops"]},
    "staking": {"weight": 1, "aliases": ["stake"]},
    "yield farming": {"weight": 1, "aliases": []},
    "liquidity mining": {"weight": 1, "aliases": []},
    "dex": {"weight": 1, "aliases": ["decentralized exchange"]},
    "cex": {"weight": 1, "aliases": ["centralized exchange"]},
    "market cap": {"weight": 1, "aliases": ["market capitalization"]},
    "circulating supply": {"weight": 1, "aliases": []},
    "token swap": {"weight": 1, "aliases": []},
    "vesting schedule": {"weight": 1, "aliases": []},

    # --- Smart contracts / programmation ---
    "smart contract": {"weight": 3, "aliases": ["smart contracts"]},
    "solidity": {"weight": 3, "aliases": []},
    "vyper": {"weight": 3, "aliases": []},
    "contract abi": {"weight": 3, "aliases": ["abi", "application binary interface"]},
    "gas": {"weight": 3, "aliases": []},
    "gas limit": {"weight": 3, "aliases": []},
    "gas price": {"weight": 3, "aliases": []},
    "deployment": {"weight": 3, "aliases": ["deploy"]},
    "event logging": {"weight": 3, "aliases": []},
    "function call": {"weight": 3, "aliases": ["function calls"]},
    "modifier": {"weight": 3, "aliases": ["modifiers"]},
    "constructor": {"weight": 3, "aliases": []},
    "interface": {"weight": 3, "aliases": ["interfaces"]},
    "inheritance": {"weight": 3, "aliases": []},
    "library contract": {"weight": 3, "aliases": ["library"]},
    "oracles": {"weight": 3, "aliases": ["oracle"]},
    "chainlink": {"weight": 3, "aliases": []},
    "dapp": {"weight": 3, "aliases": ["decentralized application", "d apps", "d-apps"]},
    "bytecode": {"weight": 3, "aliases": []},
    "storage slot": {"weight": 3, "aliases": []},
    "state variable": {"weight": 3, "aliases": []},
    "fallback function": {"weight": 3, "aliases": []},
    "revert": {"weight": 3, "aliases": []},
    "require": {"weight": 3, "aliases": []},
    "assert": {"weight": 3, "aliases": []},
    "mapping": {"weight": 3, "aliases": ["mappings"]},
    "struct": {"weight": 3, "aliases": ["structure", "structures"]},
    "enum": {"weight": 3, "aliases": ["enumeration", "enumerations"]},
    "loop": {"weight": 3, "aliases": ["loops"]},

    # --- Layer 1 / Layer 2 / scaling ---
    "layer 1": {"weight": 2, "aliases": ["l1"]},
    "layer 2": {"weight": 2, "aliases": ["l2"]},
    "sidechain": {"weight": 2, "aliases": ["side chain", "side chains"]},
    "rollup": {"weight": 2, "aliases": ["rollups"]},
    "optimistic rollup": {"weight": 2, "aliases": ["optimistic rollups"]},
    "zk-rollup": {"weight": 2, "aliases": ["zk rollup", "zk rollups"]},
    "sharding": {"weight": 2, "aliases": ["shard", "shards"]},
    "plasma": {"weight": 2, "aliases": []},
    "state channel": {"weight": 2, "aliases": ["state channels"]},
    "lightning network": {"weight": 2, "aliases": []},
    "interoperability protocol": {"weight": 2, "aliases": []},
    "cross-chain bridge": {"weight": 2, "aliases": ["bridge", "bridges", "cross chain bridge"]},
    "transaction throughput": {"weight": 2, "aliases": []},
    "scalability": {"weight": 2, "aliases": ["scalable"]},

    # --- DeFi et finance décentralisée ---
    "lending protocol": {"weight": 2, "aliases": []},
    "borrowing": {"weight": 2, "aliases": ["borrow"]},
    "collateral": {"weight": 2, "aliases": []},
    "liquidation": {"weight": 2, "aliases": ["liquidate"]},
    "flash loan": {"weight": 2, "aliases": ["flash loans"]},
    "amm": {"weight": 2, "aliases": ["automated market maker"]},
    "pool": {"weight": 2, "aliases": ["pools"]},
    "swap": {"weight": 2, "aliases": ["swaps"]},
    "impermanent loss": {"weight": 2, "aliases": []},
    "tvl": {"weight": 2, "aliases": ["total value locked"]},
    "synthetic asset": {"weight": 2, "aliases": ["synth"]},
    "stable swap": {"weight": 2, "aliases": []},
    "interest rate model": {"weight": 2, "aliases": []},
    "collateralization ratio": {"weight": 2, "aliases": []},
    "overcollateralization": {"weight": 2, "aliases": []},

    # --- Security / Attacks ---
    "51% attack": {"weight": 2, "aliases": ["majority attack"]},
    "sybil attack": {"weight": 2, "aliases": ["sybil attacks"]},
    "double spend": {"weight": 2, "aliases": ["double spending"]}, # Variante sans tiret
    "reentrancy": {"weight": 2, "aliases": ["re-entrancy"]},
    "front-running": {"weight": 2, "aliases": ["front running"]},
    "mev": {"weight": 2, "aliases": ["maximal extractable value", "miner extractable value"]},
    "rug pull": {"weight": 2, "aliases": ["rugpull"]},
    "smart contract audit": {"weight": 2, "aliases": ["audit", "audits"]},
    "cold wallet": {"weight": 2, "aliases": ["cold storage"]},
    "hot wallet": {"weight": 2, "aliases": ["hot storage"]},
    "multisig": {"weight": 2, "aliases": ["multi signature"]},
    "private key leak": {"weight": 2, "aliases": []},
    "phishing": {"weight": 2, "aliases": ["phish"]},
    "exploit": {"weight": 2, "aliases": ["exploits"]},
    "vulnerability": {"weight": 2, "aliases": ["vulnerabilities"]},
    "replay attack": {"weight": 2, "aliases": []},
    "denial of service": {"weight": 2, "aliases": ["dos"]},

    # --- Projects / Protocols populaires ---
    "bitcoin": {"weight": 1, "aliases": ["btc"]},
    "ethereum": {"weight": 1, "aliases": ["eth"]},
    "polkadot": {"weight": 1, "aliases": ["dot"]},
    "solana": {"weight": 1, "aliases": ["sol"]},
    "cardano": {"weight": 1, "aliases": ["ada"]},
    "avalanche": {"weight": 1, "aliases": ["avax"]},
    "chainlink": {"weight": 1, "aliases": ["link"]}, # Doublon, mais on le garde
    "uniswap": {"weight": 1, "aliases": []},
    "aave": {"weight": 1, "aliases": []},
    "compound": {"weight": 1, "aliases": []},
    "makerdao": {"weight": 1, "aliases": ["maker dao"]},
    "sushiswap": {"weight": 1, "aliases": ["sushi swap"]},
    "curve finance": {"weight": 1, "aliases": ["curve"]},
    "yearn finance": {"weight": 1, "aliases": ["yearn"]},
    "fantom": {"weight": 1, "aliases": ["ftm"]},

    # --- Concepts spécifiques à Ethereum/Solana/AI ---
    "artificial intelligence": {"weight": 2, "aliases": ["ai"]},
    "natural language processing": {"weight": 2, "aliases": ["nlp"]},
    "computer vision": {"weight": 2, "aliases": []},
    "human-computer interaction": {"weight": 2, "aliases": []},
    "tokenomics": {"weight": 2, "aliases": []},
    "governance": {"weight": 2, "aliases": []},
    "dao": {"weight": 2, "aliases": ["decentralized autonomous organization"]},
    "off-chain": {"weight": 2, "aliases": []},
    "on-chain": {"weight": 2, "aliases": []},
    "atomic swap": {"weight": 2, "aliases": []},
    "peg": {"weight": 2, "aliases": ["pegged"]},
    "wrapped token": {"weight": 2, "aliases": ["wrapped tokens"]},
    "cross-chain": {"weight": 2, "aliases": ["cross chain"]},
    "merkle proof": {"weight": 2, "aliases": []},
    "block reward": {"weight": 2, "aliases": []},
    "difficulty adjustment": {"weight": 2, "aliases": []},
    "inflation": {"weight": 2, "aliases": []},
    "deflation": {"weight": 2, "aliases": []},
    "gas fee optimization": {"weight": 2, "aliases": []},
    "validator set": {"weight": 2, "aliases": []},
    "epoch": {"weight": 2, "aliases": ["epochs"]},
    "slashing": {"weight": 2, "aliases": []},
    "delegation": {"weight": 2, "aliases": ["delegate"]},
    "reward distribution": {"weight": 2, "aliases": []},
    "hard cap": {"weight": 2, "aliases": []},
    "soft cap": {"weight": 2, "aliases": []},
    "vesting": {"weight": 2, "aliases": ["vest"]},
    "burn mechanism": {"weight": 2, "aliases": []},
    "snapshot": {"weight": 2, "aliases": ["snapshots"]},
    "liquidity pool token": {"weight": 2, "aliases": []},
    "orphan block": {"weight": 2, "aliases": ["uncle block"]},
    "finality": {"weight": 2, "aliases": ["finalized"]},
    "epoch length": {"weight": 2, "aliases": []},
    "governance proposal": {"weight": 2, "aliases": []},
    "voting power": {"weight": 2, "aliases": []},
    "quorum": {"weight": 2, "aliases": []},
    "inflationary mining": {"weight": 2, "aliases": []},
    "token burn rate": {"weight": 2, "aliases": []},
    "smart contract upgrade": {"weight": 2, "aliases": []},
    "proxy contract": {"weight": 2, "aliases": []},
    "testnet": {"weight": 2, "aliases": ["test net"]},
    "mainnet": {"weight": 2, "aliases": ["main net"]},
    "faucet": {"weight": 2, "aliases": ["faucets"]},
    "peer discovery": {"weight": 2, "aliases": []},
    "network topology": {"weight": 2, "aliases": []},
    "gas optimization": {"weight": 2, "aliases": []},
    "light node": {"weight": 2, "aliases": ["light client"]},
    "full node": {"weight": 2, "aliases": ["full client"]},
    "validator rotation": {"weight": 2, "aliases": []},
    "consensus algorithm": {"weight": 2, "aliases": ["consensus algorithms"]},
    "proof of stake": {"weight": 2, "aliases": ["pos", "proof-of-stake"]},
    "delegated proof of stake": {"weight": 2, "aliases": ["dpos"]},
    "proof of authority": {"weight": 2, "aliases": ["poa"]},
    "byzantine fault tolerance": {"weight": 2, "aliases": ["bft"]},
    "practical bft": {"weight": 2, "aliases": ["pbft"]},
    "chain finality": {"weight": 2, "aliases": []},
    "oracles aggregation": {"weight": 2, "aliases": []},
    "token vesting": {"weight": 2, "aliases": []},
    "smart contract interoperability": {"weight": 2, "aliases": []},
    "decentralized identity": {"weight": 2, "aliases": ["did"]},
    "non-fungible token": {"weight": 2, "aliases": ["nft", "nfts"]},
    "fungible token": {"weight": 2, "aliases": ["ft"]},
    "metadata": {"weight": 2, "aliases": []},
    # Concepts spécifiques à Solana (exemples)
    "proof of history": {"weight": 3, "aliases": ["poh"]},
    "turbine": {"weight": 2, "aliases": []},
    "gulf stream": {"weight": 2, "aliases": []},
    "sealevel": {"weight": 2, "aliases": []},
    # Concepts spécifiques à Cogni AI
    "cogni ai": {"weight": 2, "aliases": ["cogni"]},
}

def normalize_text_for_analysis(text: str) -> str:
    """
    Normalise le texte pour l'analyse : minuscules, espaces cohérents, etc.
    """
    if not text:
        return ""
    # 1. Minuscules
    text = text.lower()
    # 2. Normaliser les espaces et certains tirets
    # Remplacer les tirets isolés ou entourés de lettres par des espaces
    # Ceci aidera à faire correspondre "sha-256" avec "sha 256" ou "sha256"
    # On évite de casser les nombres décimaux comme 1.5
    # Tiret entre deux lettres ou chiffres -> espace
    text = re.sub(r'(?<=[a-zA-Z0-9])-(?=[a-zA-Z0-9])', ' ', text)
    # 3. Supprimer la ponctuation sauf les points (pour les décimaux) et les espaces
    # On veut garder les mots séparés par des espaces
    text = re.sub(r'[^\w\s.]', ' ', text)
    # 4. Remplacer les espaces multiples par un seul espace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def calculate_technical_score(text: str, terms_dict: Dict[str, Dict] = TECH_TERMS) -> Dict[str, Union[float, int, Dict]]:
    """
    Calcule un score de technicité basé sur un dictionnaire de termes avec variantes.
    """
    if not text:
        return {
            "score_normalise": 0.0,
            "score_brut": 0,
            "total_mots": 0,
            "details_par_categorie": {},
            "termes_trouves": {}
        }

    # 1. Normaliser le texte
    normalized_text = normalize_text_for_analysis(text)
    words = normalized_text.split()
    total_words = len(words)
    
    if total_words == 0:
        return {
            "score_normalise": 0.0,
            "score_brut": 0,
            "total_mots": 0,
            "details_par_categorie": {},
            "termes_trouves": {}
        }

    score_brut = 0
    termes_comptes = {} # Stockera le terme canonique et son compte

    # Parcourir chaque terme canonique et ses variantes
    for canonical_term, term_info in terms_dict.items():
        weight = term_info.get("weight", 1)
        aliases = term_info.get("aliases", [])
        
        # Créer une liste de toutes les formes à rechercher (terme canonique + alias)
        search_terms = [canonical_term] + aliases
        total_count_for_term = 0
        
        # Normaliser chaque terme de recherche et chercher dans le texte
        for search_term in search_terms:
            norm_search_term = normalize_text_for_analysis(search_term)
            # Utiliser \b pour les limites de mots
            pattern = r'\b' + re.escape(norm_search_term) + r'\b'
            matches = re.findall(pattern, normalized_text)
            count = len(matches)
            total_count_for_term += count
            
        if total_count_for_term > 0:
            score_brut += total_count_for_term * weight
            # Stocker le terme canonique pour l'affichage
            termes_comptes[canonical_term] = total_count_for_term
            
    score_normalized = (score_brut / total_words) * 100 if total_words > 0 else 0
    
    return {
        "score_normalise": round(score_normalized, 2),
        "score_brut": score_brut,
        "total_mots": total_words,
        "details_par_categorie": {}, # Placeholder pour une analyse plus fine
        "termes_trouves": termes_comptes
    }

# Exemple d'utilisation (facultatif)
if __name__ == "__main__":
    # Exemple avec le texte du COGNI AI fourni
    sample_text = """
    Welcome to the COGNI AI whitepaper, an innovative project aiming to revolutionize the interaction between humans and computers through advancements in artificial intelligence (AI). In this document, we will explore the details of COGNI AI, from its vision to its technical implementation, covering the services offered, technological architecture, and token economy.
    Imagine the Future with COGNI AI
    COGNI AI emerges as a response to contemporary challenges faced at the intersection of humans and technology. With the advent of artificial intelligence, we have witnessed significant advancements in areas such as natural language processing (NLP) and computer vision. COGNI AI seeks to transcend these advancements, providing deeper and more meaningful interactions between humans and machines.
    """
    result = calculate_technical_score(sample_text)
    print("Résultat de l'analyse de technicité (exemple):")
    print(f"  Score normalisé: {result['score_normalise']}")
    print(f"  Score brut: {result['score_brut']}")
    print(f"  Nombre de mots: {result['total_mots']}")
    print("  Termes trouvés:")
    for term, count in list(result['termes_trouves'].items())[:10]: # Afficher les 10 premiers #type:ignore
        print(f"    - {term}: {count}")
