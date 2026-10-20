"""시범 네 작품(데스티니·스텔라리스·듄·에반게리온)에서 올라온 개념 제안 15건을 14개 개념으로 합쳐 넣고,
제안에 적힌 용어들을 새 개념에 잇는다. 한 번만 돌린다(이미 있으면 건너뜀).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

NEW = [
    {"id": "machine_race", "ko": "기계 종족", "en": "Machine race", "cat": "life", "parent": "alien",
     "one": "기계 몸을 가진 채 스스로 퍼지며 문명을 이루는 종족.",
     "note": "처음에 누가 만들었는지와 상관없이, 지금은 스스로 늘고 스스로 뜻을 세운다. 행성을 통째로 기계로 바꾸거나 유기 생명을 없애려는 모습으로 자주 그려진다.",
     "similar": [{"id": "ai", "how": "인공지능은 누군가 만들어 부리는 기계 지성이고, 기계 종족은 스스로 퍼지는 기계 문명이다."}]},
    {"id": "elder_race", "ko": "아직 남은 옛 문명", "en": "Elder race", "cat": "life", "parent": "alien",
     "one": "아득히 앞선 기술을 쥔 채 물러나 있는, 아직 살아 있는 고대 문명.",
     "note": "젊은 문명들 위에 조용히 앉아 지켜보거나 간섭한다. 오래 멈춰 있다가 깨어나는 순간이 큰 사건이 된다.",
     "similar": [{"id": "precursor", "how": "사라진 옛 문명은 이미 없고, 아직 남은 옛 문명은 살아서 물러나 있다."}]},
    {"id": "living_machine", "ko": "길러 낸 배와 병기", "en": "Living ships and weapons", "cat": "life", "parent": None,
     "one": "기계로 짓지 않고 생명을 만들어 내거나 길러서 배나 병기로 쓰는 것.",
     "note": "피를 흘리고 자라고 스스로 움직이기도 해서, 다루는 사람이 그것을 다 통제하지 못한다는 두려움이 따른다.",
     "similar": [{"id": "mecha", "how": "타고 싸우는 거대 로봇은 기계이고, 길러 낸 병기는 생명이다."}]},
    {"id": "antigravity", "ko": "반중력", "en": "Antigravity", "cat": "move", "parent": None,
     "one": "무게를 거슬러 물건이나 탈것을 공중에 띄우는 기술.",
     "note": "바퀴 없이 떠다니는 탈것과 짐, 떠 있는 도시 같은 미래의 풍경을 만든다.",
     "similar": []},
    {"id": "simulation", "ko": "모의 현실", "en": "Simulated reality", "cat": "machine", "parent": None,
     "one": "기계가 세계나 사람을 통째로 본떠 계산해 낸, 안에서는 진짜와 구별되지 않는 세계.",
     "note": "가상 세계에 들어가는 이야기도, 지금 이 세계가 사실은 계산된 것이라는 이야기도 있다. 무엇이 진짜인가가 물음이 된다.",
     "similar": [{"id": "mind_upload", "how": "의식 옮기기는 사람이 기계 속으로 들어가는 것이고, 모의 현실은 세계 자체가 계산된 것이다."},
                 {"id": "alt_timeline", "how": "평행 세계는 실제로 따로 있는 세계이고, 모의 현실은 계산으로 만든 세계다."}]},
    {"id": "ancestral_memory", "ko": "물려받는 기억", "en": "Ancestral memory", "cat": "mind", "parent": None,
     "one": "조상들이 겪은 삶과 기억을 핏줄이나 의식을 거쳐 물려받아 지니는 것.",
     "note": "수많은 옛사람의 지혜를 빌릴 수 있지만, 그 목소리들에 자기가 먹힐 위험이 함께 온다.",
     "similar": [{"id": "mind_upload", "how": "의식 옮기기는 한 사람의 마음을 옮기는 것이고, 물려받는 기억은 핏줄로 이어진 여러 사람의 기억이다."}]},
    {"id": "awakening_substance", "ko": "능력을 깨우는 물질", "en": "Ability-awakening substance", "cat": "mind", "parent": None,
     "one": "몸에 들이면 초능력이나 예지를 깨우거나 키워 주는 귀한 물질.",
     "note": "힘을 주는 대신 중독이나 몸의 변화를 부르는 경우가 많고, 그 물질을 쥔 쪽이 능력자를 쥔다.",
     "similar": [{"id": "key_resource", "how": "모든 것이 걸린 물질은 귀해서 다툼의 대상이고, 능력을 깨우는 물질은 몸에 들여 힘을 얻는 것이다. 둘을 겸하는 물질도 많다."}]},
    {"id": "pact", "ko": "강대한 존재와의 계약", "en": "Pact with a greater being", "cat": "mind", "parent": None,
     "one": "사람 너머의 강대한 존재에게 힘을 받는 대신 그 뜻에 묶이는 약속.",
     "note": "얻는 힘이 클수록 치를 값도 커서, 언젠가 그 값을 받으러 온다. 상대는 다른 차원의 존재일 때가 많다.",
     "similar": [{"id": "other_realm", "how": "또 하나의 차원은 그곳 자체이고, 계약은 그곳의 존재와 맺는 거래다."}]},
    {"id": "flotilla", "ko": "떠도는 함대 사회", "en": "Flotilla society", "cat": "society", "parent": None,
     "one": "행성에 뿌리내리지 않고 배를 집 삼아 옮겨 다니며 사는 사회.",
     "note": "고향을 잃었거나 처음부터 갖지 않은 사람들이다. 물과 공기와 자리가 모자라 배 안의 규율이 엄해진다.",
     "similar": [{"id": "generation_ship", "how": "세대선은 목적지가 있는 배 한 척이고, 떠도는 함대 사회는 배들이 곧 사는 곳이다."},
                 {"id": "spacers", "how": "우주에서 자란 인류는 거주지에 정착해 살고, 떠도는 함대 사회는 머물 곳 없이 옮겨 다닌다."}]},
    {"id": "long_plan", "ko": "대를 잇는 긴 계획", "en": "Plan spanning millennia", "cat": "history", "parent": None,
     "one": "한 사람이나 집단이 수백, 수천 년 뒤를 내다보고 세워 대를 이어 밀고 가는 계획.",
     "note": "계획한 사람은 그 끝을 보지 못하고, 계획을 따르는 사람은 그것을 모르는 경우가 많다. 계획이 틀어지는 순간이 이야기가 된다.",
     "similar": [{"id": "psychohistory", "how": "미래를 계산하는 학문은 앞날을 따지는 방법이고, 대를 잇는 긴 계획은 그 앞날을 바꾸려고 세운 일이다."}]},
    {"id": "cloaking", "ko": "모습을 감추는 기술", "en": "Cloaking", "cat": "war", "parent": None,
     "one": "배나 사람을 눈과 탐지 장치에서 감추는 기술.",
     "note": "보이지 않는 적이 싸움의 셈법을 바꾼다. 감추는 쪽과 찾는 쪽의 기술 다툼이 이어진다.",
     "similar": []},
    {"id": "single_biome", "ko": "한 가지 환경뿐인 행성", "en": "Single-biome planet", "cat": "world", "parent": None,
     "one": "행성 전체가 사막이나 얼음, 바다처럼 한 가지 환경으로만 된 곳.",
     "note": "그 환경이 거기 사는 사람들의 몸과 관습과 신앙을 통째로 빚는다.",
     "similar": [{"id": "terraforming", "how": "한 가지 환경뿐인 행성은 있는 그대로의 모습이고, 테라포밍은 그것을 바꾸는 일이다."}]},
    {"id": "benefactor", "ko": "문명을 길러 주는 존재", "en": "Benefactor of civilizations", "cat": "cosmos", "parent": None,
     "one": "젊은 문명에 찾아와 땅과 기술과 번영을 내려 주며 그 운명을 바꾸는 바깥의 존재.",
     "note": "받은 쪽은 그 존재에 기대게 되고, 그 존재를 쫓는 적까지 함께 떠안기도 한다. 왜 돕는지는 대개 끝까지 알 수 없다.",
     "similar": [{"id": "uplift", "how": "지성 끌어올리기는 지성이 없던 것을 지성 있게 만드는 것이고, 문명을 길러 주는 존재는 이미 있는 문명을 키워 주는 것이다."},
                 {"id": "godlike", "how": "신에 가까운 존재는 힘의 크기를 말하고, 문명을 길러 주는 존재는 그 힘으로 하는 일을 말한다."}]},
    {"id": "galactic_threat", "ko": "모든 문명을 덮치는 위협", "en": "Galaxy-wide threat", "cat": "cosmos", "parent": None,
     "one": "은하 바깥이나 다른 차원, 오래된 기계에서 나타나 모든 문명의 존속을 위협하는 적.",
     "note": "협상이 통하지 않아, 서로 다투던 문명들이 손을 잡느냐가 물음이 된다.",
     "similar": [{"id": "cycle", "how": "되풀이되는 멸망은 주기가 있고, 모든 문명을 덮치는 위협은 한 번 닥치는 적이다."}]},
]

LINKS = {
    "destiny": {"vex": ["machine_race"], "infinite_forest": ["simulation"], "traveler": ["benefactor"],
                "long_drift": ["flotilla"], "worm": ["pact"]},
    "stellaris": {"fallen_empire": ["elder_race"], "awakened_empire": ["elder_race"], "ancient_caretakers": ["elder_race"],
                  "war_in_heaven": ["elder_race"], "bioships": ["living_machine"], "prethoryn_scourge": ["living_machine", "galactic_threat"],
                  "nomadic_empire": ["flotilla"], "arkship": ["flotilla"], "caravaneers": ["flotilla"],
                  "endgame_crisis": ["galactic_threat"], "contingency": ["galactic_threat", "machine_race"], "unbidden": ["galactic_threat"],
                  "gray_tempest": ["galactic_threat"], "become_the_crisis": ["galactic_threat"],
                  "covenant": ["pact"], "shroud_patron": ["pact"], "end_of_the_cycle": ["pact"],
                  "zro": ["awakening_substance"], "vultaum": ["simulation"]},
    "dune": {"suspensor": ["antigravity"], "other_memory": ["ancestral_memory"], "abomination": ["ancestral_memory"],
             "golden_path": ["long_plan"], "breeding_program": ["long_plan"], "no_ship": ["cloaking"],
             "arrakis": ["single_biome"], "spice_melange": ["awakening_substance"]},
    "evangelion": {k: ["living_machine"] for k in ["evangelion", "eva_unit_00", "eva_unit_01", "eva_unit_02",
                                                    "eva_unit_03", "eva_unit_04", "mass_production_eva"]},
}


def main():
    p = DATA / "concepts.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    have = {c["id"] for c in d["concepts"]}
    parents = {c["id"]: c.get("parent") for c in d["concepts"]}
    added = 0
    for c in NEW:
        if c["id"] not in have:
            d["concepts"].append(c)
            parents[c["id"]] = c.get("parent")
            added += 1
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def ancestors(cid):
        out, cur = set(), parents.get(cid)
        while cur:
            out.add(cur)
            cur = parents.get(cur)
        return out

    linked = 0
    for work, m in LINKS.items():
        tp = DATA / "terms" / f"{work}.json"
        td = json.loads(tp.read_text(encoding="utf-8"))
        for t in td["terms"]:
            for cid in m.get(t["id"], []):
                if cid not in t["concepts"]:
                    t["concepts"].append(cid)
                    linked += 1
                # 새로 단 개념의 상위가 이미 달려 있으면 빼서 가장 좁은 것만 남긴다
                for a in ancestors(cid):
                    if a in t["concepts"]:
                        t["concepts"].remove(a)
        tp.write_text(json.dumps(td, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"새 개념 {added}개, 새로 이은 자리 {linked}개")


if __name__ == "__main__":
    main()
