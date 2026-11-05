"""Original inline SVG character artwork for The Call."""

def _svg_commentator(talking: bool = False) -> str:
    state = "is-talking" if talking else ""
    return f"""<svg class="avatar talker {state}" viewBox="0 0 180 190" role="img" aria-label="Animated illustrated sports commentator">
      <ellipse cx="90" cy="178" rx="54" ry="7" fill="#756D47" opacity=".22"/>
      <path d="M28 178 Q31 130 62 119 L118 119 Q149 132 152 178Z" fill="#674550"/>
      <path d="M66 124 L90 150 L114 124 L108 178 L72 178Z" fill="#FFF9EF"/>
      <path d="M84 148 L90 156 L96 148 L103 178 L77 178Z" fill="#756D47"/>
      <g class="head">
        <path d="M48 75 Q44 22 91 20 Q138 22 132 81 L125 113 Q115 136 90 137 Q64 135 54 112Z" fill="#B97852"/>
        <path d="M48 71 Q40 24 88 15 Q128 10 139 54 Q118 34 93 37 Q69 37 51 65Z" fill="#3F2932"/>
        <path d="M53 72 Q43 83 52 95 Q59 101 63 89Z" fill="#B97852"/>
        <path d="M128 72 Q139 83 129 95 Q122 101 118 89Z" fill="#B97852"/>
        <path d="M67 78 Q75 73 83 78 M99 78 Q107 73 115 78" stroke="#3F2932" stroke-width="4" fill="none" stroke-linecap="round"/>
        <ellipse cx="76" cy="88" rx="4" ry="5" fill="#3F2932"/><ellipse cx="106" cy="88" rx="4" ry="5" fill="#3F2932"/>
        <path d="M88 91 Q82 105 91 106" fill="none" stroke="#8E523B" stroke-width="2.5" stroke-linecap="round"/>
        <path class="mouth" d="M78 115 Q90 124 103 114 Q91 132 78 115Z" fill="#3F2932"/>
        <path d="M45 65 Q42 30 72 20 M136 65 Q140 30 110 20" stroke="#756D47" stroke-width="8" fill="none" stroke-linecap="round"/>
        <rect x="39" y="65" width="14" height="34" rx="7" fill="#756D47"/><rect x="127" y="65" width="14" height="34" rx="7" fill="#756D47"/>
      </g>
      <path d="M129 107 Q147 105 151 119" stroke="#3F2932" stroke-width="4" fill="none" stroke-linecap="round"/>
      <circle cx="151" cy="120" r="5" fill="#756D47"/>
      <path d="M30 152 Q14 145 14 130 M150 152 Q166 145 165 127" stroke="#B97852" stroke-width="12" stroke-linecap="round" fill="none"/>
      <circle cx="14" cy="127" r="8" fill="#B97852"/><circle cx="166" cy="124" r="8" fill="#B97852"/>
    </svg>"""

def _svg_batter() -> str:
    return """<svg class="avatar" viewBox="0 0 150 170" role="img" aria-label="Cricket batter character">
      <ellipse cx="78" cy="160" rx="43" ry="6" fill="#756D47" opacity=".22"/>
      <path d="M50 84 Q30 95 34 140 L48 156 L106 156 L119 136 Q119 101 99 84Z" fill="#756D47"/>
      <path d="M62 87 L78 113 L95 87 L101 151 L55 151Z" fill="#E9D8B9"/>
      <path d="M52 90 Q35 80 45 69 L60 76Z M100 88 Q115 77 109 67 L94 77Z" fill="#756D47"/>
      <path d="M51 45 Q50 16 78 16 Q106 17 105 48 L99 78 Q92 91 78 91 Q62 90 56 76Z" fill="#B97852"/>
      <path d="M48 46 Q41 15 77 10 Q112 9 111 43 L99 35 L61 36Z" fill="#674550"/>
      <path d="M49 42 Q77 33 108 43" stroke="#F0DEBD" stroke-width="7" fill="none"/>
      <circle cx="69" cy="53" r="3.2" fill="#3F2932"/><circle cx="89" cy="53" r="3.2" fill="#3F2932"/>
      <path d="M70 68 Q79 75 88 67" stroke="#3F2932" stroke-width="2.5" fill="none" stroke-linecap="round"/>
      <path d="M114 30 L139 135" stroke="#A66C3E" stroke-width="9" stroke-linecap="round"/>
      <path d="M108 22 L121 17 L129 49 L116 53Z" fill="#674550"/>
      <path d="M40 137 L25 154 M109 138 L124 154" stroke="#3F2932" stroke-width="9" stroke-linecap="round"/>
      <path d="M24 156 L13 158 M123 156 L137 158" stroke="#674550" stroke-width="8" stroke-linecap="round"/>
    </svg>"""

def _svg_bowler() -> str:
    return """<svg class="avatar" viewBox="0 0 150 170" role="img" aria-label="Cricket bowler character">
      <ellipse cx="76" cy="160" rx="42" ry="6" fill="#756D47" opacity=".22"/>
      <path d="M45 84 Q24 102 31 145 L49 157 L104 157 L121 139 Q117 100 98 84Z" fill="#674550"/>
      <path d="M61 86 L76 109 L94 86 L101 151 L52 151Z" fill="#F0DEBD"/>
      <path d="M47 93 Q19 82 28 52 Q31 43 39 48 Q46 65 59 73Z" fill="#B97852" stroke="#B97852" stroke-width="8" stroke-linecap="round"/>
      <path d="M100 92 Q123 76 112 51" fill="none" stroke="#B97852" stroke-width="12" stroke-linecap="round"/>
      <circle cx="111" cy="47" r="7" fill="#B97852"/>
      <path d="M52 45 Q51 17 77 16 Q103 16 104 47 L98 76 Q91 90 77 90 Q61 88 56 74Z" fill="#B97852"/>
      <path d="M49 46 Q47 15 79 11 Q105 13 110 42 Q82 32 53 43Z" fill="#3F2932"/>
      <circle cx="68" cy="51" r="3" fill="#3F2932"/><circle cx="89" cy="51" r="3" fill="#3F2932"/>
      <path d="M67 68 Q77 73 87 67" stroke="#3F2932" stroke-width="2.5" fill="none" stroke-linecap="round"/>
      <circle cx="124" cy="32" r="8" fill="#674550"/><path d="M120 28 Q125 29 128 35" stroke="#F0DEBD" stroke-width="1.5" fill="none"/>
      <path d="M48 139 L38 157 M103 139 L113 157" stroke="#3F2932" stroke-width="9" stroke-linecap="round"/>
      <path d="M36 158 L23 159 M113 158 L127 159" stroke="#756D47" stroke-width="8" stroke-linecap="round"/>
    </svg>"""

def _svg_striker() -> str:
    return """<svg class="avatar" viewBox="0 0 150 170" role="img" aria-label="Football striker character">
      <ellipse cx="77" cy="160" rx="43" ry="6" fill="#756D47" opacity=".22"/>
      <path d="M48 82 Q29 92 32 137 L50 152 L105 152 L120 133 Q114 100 98 82Z" fill="#674550"/>
      <path d="M59 85 L76 110 L94 85 L101 149 L52 149Z" fill="#F0DEBD"/>
      <path d="M49 92 L28 120 M101 91 L119 118" stroke="#B97852" stroke-width="11" stroke-linecap="round"/>
      <path d="M50 43 Q49 15 77 15 Q105 16 105 47 L99 75 Q92 88 77 88 Q62 87 56 75Z" fill="#B97852"/>
      <path d="M49 42 Q48 14 78 11 Q105 12 110 42 Q79 33 51 43Z" fill="#3F2932"/>
      <circle cx="68" cy="51" r="3" fill="#3F2932"/><circle cx="89" cy="51" r="3" fill="#3F2932"/>
      <path d="M68 67 Q77 74 87 67" stroke="#3F2932" stroke-width="2.5" fill="none" stroke-linecap="round"/>
      <path d="M56 142 L49 159 M101 142 L112 157" stroke="#3F2932" stroke-width="9" stroke-linecap="round"/>
      <path d="M47 158 L31 160 M110 157 L129 160" stroke="#674550" stroke-width="8" stroke-linecap="round"/>
      <circle cx="124" cy="139" r="13" fill="#FFF9EF" stroke="#3F2932" stroke-width="2"/>
      <path d="M124 131 L129 136 L126 144 L119 144 L117 137Z" fill="#674550"/>
    </svg>"""

def _svg_keeper() -> str:
    return """<svg class="avatar" viewBox="0 0 150 170" role="img" aria-label="Football goalkeeper character">
      <ellipse cx="77" cy="160" rx="43" ry="6" fill="#756D47" opacity=".22"/>
      <path d="M45 83 Q20 100 31 144 L49 155 L105 155 L122 140 Q118 103 99 83Z" fill="#756D47"/>
      <path d="M60 84 L77 109 L95 84 L102 151 L52 151Z" fill="#F0DEBD"/>
      <path d="M47 97 Q25 83 17 65 M102 97 Q125 82 133 62" stroke="#B97852" stroke-width="13" fill="none" stroke-linecap="round"/>
      <circle cx="15" cy="61" r="12" fill="#674550"/><circle cx="135" cy="59" r="12" fill="#674550"/>
      <path d="M49 43 Q49 16 77 15 Q105 16 105 46 L99 75 Q91 89 77 89 Q62 87 56 75Z" fill="#B97852"/>
      <path d="M49 42 Q48 14 78 11 Q105 12 110 42 Q79 33 51 43Z" fill="#3F2932"/>
      <circle cx="68" cy="51" r="3" fill="#3F2932"/><circle cx="89" cy="51" r="3" fill="#3F2932"/>
      <path d="M67 68 Q77 74 88 68" stroke="#3F2932" stroke-width="2.5" fill="none" stroke-linecap="round"/>
      <path d="M55 141 L49 159 M99 141 L108 159" stroke="#3F2932" stroke-width="9" stroke-linecap="round"/>
      <path d="M48 159 L32 161 M107 159 L123 161" stroke="#674550" stroke-width="8" stroke-linecap="round"/>
    </svg>"""

