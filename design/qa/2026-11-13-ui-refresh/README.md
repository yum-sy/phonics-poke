# 포켓몬 UI 이식 검증

데스크톱Chrome검증이며 실기기확인은아니다. iPad최초124/128→이름수정8건으로 최종128/128, Fold128/128. 이후 전체136빌런이름×4화면544건검사로 이름크기최종38/18px확정. 기존측정보고서와수정결과를함께보관했다.
부모화면12, production부모제스처10/진도편집13/설치검수5 통과. 포켓몬아트·4마리합체·GIF·학습·음원보존. 최종글꼴로여러줄제목제스처검증포함.
재현: scripts/check-safe-layout.mjs, scripts/check-pokemon-name-layout.mjs, scripts/check-parent-command-browser.mjs, scripts/check-parent-progress-browser.mjs, scripts/check-fold-install.mjs.
