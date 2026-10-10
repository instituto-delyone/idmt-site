from __future__ import annotations

import json
import re
import hashlib
import uuid
from urllib.parse import urlparse
from workers import WorkerEntrypoint

import library_runtime
from library_runtime import MEMORY_LAB, boot_library, boot_text_matrix
from http_runtime import _json_body, _request_origin, make_response
from cloudflare_bindings import binding
from storage_runtime import (
    ALLOWED_UPLOAD_TYPES,
    CHUNK_PAGES,
    D1_BINDING,
    LIBRARY_R2_PREFIX,
    MAX_UPLOAD_BYTES,
    MEDUNITY_AUTH_URL,
    R2_BINDING,
    LibraryBuilderWorkflow,
    admin_documents,
    admin_upload,
    build_document_library,
    convert_r2_pdf_to_markdown,
    make_page_chunks,
    markdown_pages,
    medunity_admin_login,
    medunity_me,
    normalize_library_text,
    plain_document,
    require_admin,
    sanitize_filename,
    storage_status,
)
from conversation_runtime import (
    FEEDBACK_CATEGORIES,
    FEEDBACK_DECISIONS,
    FEEDBACK_RATINGS,
    FEEDBACK_ROOT_CAUSES,
    MODEL_VERSION,
    _audit_admin_action,
    _clip,
    _utc_now,
    adaptive_schema_ready,
    handle_ask,
    classify_interaction,
    _safe_useful_snapshot,
)

EMBEDDED_LIBRARY_INDEXES = json.loads(r'''[{"schema_version":"1.0","builder_version":"1.0.0","source":{"name":"arquitetura-e-organizacao-computadores-8a.pdf","key":"arquitetura_organizacao_computadores","sha256":"5eac460e33281c166dd5c74532de663934f395ab916bee75c98df559ff4ae570","type":"pdf"},"chunking":{"unit":"pages","size":25,"preserves_source_text":true,"summarizes":false,"cache_policy":"private_local"},"chunks":[{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-C7BD5AB44F2D","sequence":1,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":1,"end_page":25,"text_length":69428,"text_checksum":"f5c8e2e172607676ec4af15d3c70e872a92e5056734abf01ef7cfe732c792d35","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-C7BD5AB44F2D.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-1B02DB9BC61F","sequence":2,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":26,"end_page":50,"text_length":78667,"text_checksum":"647b3d46b72363d46e37b2bdd1c69f5117e130321e3fdc62ddd1c2b96af5ee87","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-1B02DB9BC61F.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-C0B64EAB1D21","sequence":3,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":51,"end_page":75,"text_length":77677,"text_checksum":"663926a7cf3164c3d793034f93c6fbac6813ee722a60775cfed685cab5386938","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-C0B64EAB1D21.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-6A494AE01650","sequence":4,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":76,"end_page":100,"text_length":70036,"text_checksum":"16a860075be3f2b3c8c6031216efaa6ec2dbe5a0da67cdf3058a949275342438","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-6A494AE01650.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-06295063ED1D","sequence":5,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":101,"end_page":125,"text_length":67749,"text_checksum":"09f426ae123adbe2d8f24f65f7676f699b432b4e8852377fbeb7de71244ded88","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-06295063ED1D.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-143F2D77E7E1","sequence":6,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":126,"end_page":150,"text_length":87035,"text_checksum":"51f32471a1aa4ca82fd203e17d8d7b64459b7f07b95a93ed39dd45cf771e7b91","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-143F2D77E7E1.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-A92F9E9A451B","sequence":7,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":151,"end_page":175,"text_length":70489,"text_checksum":"ee20d7263c0f270aaf83fa1a94eeae77fc545b8feea8e3d6f452fe66067f5f70","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-A92F9E9A451B.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-D908DC9F8D90","sequence":8,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":176,"end_page":200,"text_length":80386,"text_checksum":"35168113a57fd82b886ac2b1fc9aaa167e871dfea6abc2bcec2c678f6f2cbc48","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-D908DC9F8D90.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-4EA5B96F140A","sequence":9,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":201,"end_page":225,"text_length":79033,"text_checksum":"fc9cbbe290d7c4589a38961fd7d09e263faeeaf8bfc99f85d8f7fdfafe0197a8","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-4EA5B96F140A.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-92620C9F0553","sequence":10,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":226,"end_page":250,"text_length":74021,"text_checksum":"905eb885d19141a8c80705a0c766a8301fba09b91cf13e3efb834157df8b033d","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-92620C9F0553.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-40B869267294","sequence":11,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":251,"end_page":275,"text_length":66824,"text_checksum":"3c1c0c5b44071fa027dea8d1d1e1160a530bf2c3b7ac255da5a57575cb3939b7","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-40B869267294.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-CE9998A6682C","sequence":12,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":276,"end_page":300,"text_length":67168,"text_checksum":"09df73643d7e500086cdc971e4aa751e909773248252ad18027af723cd594c16","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-CE9998A6682C.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-E57EC8F1F07D","sequence":13,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":301,"end_page":325,"text_length":77946,"text_checksum":"3139cce2b455466671efa135cd7e625a788ce4ac78f15e6f5af6056cae621df2","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-E57EC8F1F07D.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-EBF52220181C","sequence":14,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":326,"end_page":350,"text_length":77415,"text_checksum":"9e88ed6720b199757fc8e17400e91065beaa0478ab6dc6df502970a9c8a502a7","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-EBF52220181C.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-C8AF9B7B4A22","sequence":15,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":351,"end_page":375,"text_length":85558,"text_checksum":"a162652442d948efd486ced6469bf95ecaa243d11307a1aaacc944bd2d16b52d","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-C8AF9B7B4A22.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-9A52B29D4FCC","sequence":16,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":376,"end_page":400,"text_length":74248,"text_checksum":"d4e45b111704b846e922f0fd9834ff04ee92577515dce0e900de9aa0bfb02b71","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-9A52B29D4FCC.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-8A5686C25DD6","sequence":17,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":401,"end_page":425,"text_length":87065,"text_checksum":"92d5c439a6e042b73b99d2c3fdc19df23096c12f14a6d3875c4a9ff48857fb1b","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-8A5686C25DD6.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-C0A088BEB67B","sequence":18,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":426,"end_page":450,"text_length":75675,"text_checksum":"15f79e4d4d53632d70bc81da4803c4b32dabfd47e408138bed3e52943411f474","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-C0A088BEB67B.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-339776D6963E","sequence":19,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":451,"end_page":475,"text_length":77891,"text_checksum":"6f49b5acc30c722197caecf278197a5823d7bd5c3b99e771fc558f025e17b4a9","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-339776D6963E.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-9DEAAE995621","sequence":20,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":476,"end_page":500,"text_length":64922,"text_checksum":"be47037d4003fdf65c71ae8f1f1d7dee1ed191b503dfb562664b3651b1c26b64","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-9DEAAE995621.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-FA7E40A31EF8","sequence":21,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":501,"end_page":525,"text_length":66603,"text_checksum":"95b70d06938beb8ed1376b796331122611877dafcc61170780718cfe2aa126f8","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-FA7E40A31EF8.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-2A545793EE5C","sequence":22,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":526,"end_page":550,"text_length":82117,"text_checksum":"d78b580a667c1fc6ede9993a70cbcd4cfab54765865d2e2277f7f4c989fba934","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-2A545793EE5C.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-43D9DDB4B9C8","sequence":23,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":551,"end_page":575,"text_length":79083,"text_checksum":"3339d90edf47ab07a22f611d11bfa9cdea746cc1714c579183931605f940e532","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-43D9DDB4B9C8.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-D2FBDDBF93C6","sequence":24,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":576,"end_page":600,"text_length":76399,"text_checksum":"39e979cb680f108c1d1e59b91db8e6aae44fde4968712ebed61edcf4170276cd","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-D2FBDDBF93C6.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-DD2EB89CFCE1","sequence":25,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":601,"end_page":625,"text_length":78133,"text_checksum":"b235d16a2640c4abcf505e7aaf24f50b32b0a2329a3464671c9340e67213b453","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-DD2EB89CFCE1.txt"},{"id":"ARQUITETURA_ORGANIZACAO_COMPUTADORES-AE56892F3041","sequence":26,"source":"arquitetura-e-organizacao-computadores-8a.pdf","source_key":"arquitetura_organizacao_computadores","start_page":626,"end_page":643,"text_length":72812,"text_checksum":"77db53cb31634e2a509091f7af8725aaff927ac1b1ec0fb1ca6a12afba361fc7","cache_file":"arquitetura_organizacao_computadores\\ARQUITETURA_ORGANIZACAO_COMPUTADORES-AE56892F3041.txt"}]},{"schema_version":"1.0","builder_version":"1.0.0","source":{"name":"etica.pdf","key":"etica","sha256":"06e54c88593641072181188cc6bef92aab06aa6040d60f863fe12a12f2a0f40e","type":"pdf"},"chunking":{"unit":"pages","size":25,"preserves_source_text":true,"summarizes":false,"cache_policy":"private_local"},"chunks":[{"id":"ETICA-631B9D6E7B85","sequence":1,"source":"etica.pdf","source_key":"etica","start_page":1,"end_page":25,"text_length":53440,"text_checksum":"952ac35b8c67a9973976ea445cf8e675bd1083adf1c89967fb979e04d8905d84","cache_file":"etica\\ETICA-631B9D6E7B85.txt"},{"id":"ETICA-09EDDCC57A0C","sequence":2,"source":"etica.pdf","source_key":"etica","start_page":26,"end_page":50,"text_length":67110,"text_checksum":"224f20b68c06595514a8209ab0f9117096cb6b298dc9063c6121c49fef626579","cache_file":"etica\\ETICA-09EDDCC57A0C.txt"},{"id":"ETICA-EA2514E067DC","sequence":3,"source":"etica.pdf","source_key":"etica","start_page":51,"end_page":56,"text_length":7667,"text_checksum":"da1b40c423aedc0d9cd29e8861ab60abad15a6d30ce646dd4d497b7b1ae4319a","cache_file":"etica\\ETICA-EA2514E067DC.txt"}]},{"schema_version":"1.0","builder_version":"1.0.0","source":{"name":"interações DrDelyone-AIGAR.txt","key":"interacoes_aigar","sha256":"29c97629bec3fb0b7d6cdfb1b4c0492f2587c459b952aaae5e06b6a57b1769f7","type":"txt"},"chunking":{"unit":"characters","size":24000,"preserves_source_text":true,"summarizes":false,"cache_policy":"private_local"},"chunks":[{"id":"INTERACOES_AIGAR-BA384194F5AB","sequence":1,"source":"interações DrDelyone-AIGAR.txt","source_key":"interacoes_aigar","start_page":null,"end_page":null,"text_length":5556,"text_checksum":"aab6e84d38f302abe177b28fe5b3ed686d210929cca4278e84d7bd3b30a03f34","cache_file":"interacoes_aigar\\INTERACOES_AIGAR-BA384194F5AB.txt"}]},{"schema_version":"1.0","builder_version":"1.0.0","source":{"name":"MatematicaComputacional.pdf","key":"matematica_computacional","sha256":"661b6e53ba82d101cb5033ab3f4665943cb66468b2758dcaffc5b27e5574c121","type":"pdf"},"chunking":{"unit":"pages","size":25,"preserves_source_text":true,"summarizes":false,"cache_policy":"private_local"},"chunks":[{"id":"MATEMATICA_COMPUTACIONAL-F9F9C339933C","sequence":1,"source":"MatematicaComputacional.pdf","source_key":"matematica_computacional","start_page":1,"end_page":25,"text_length":50899,"text_checksum":"e84cce0c5ce3e5f7489bf325a0536cf2733f0a807bb1d94fb7c14c944fbae0fd","cache_file":"matematica_computacional\\MATEMATICA_COMPUTACIONAL-F9F9C339933C.txt"},{"id":"MATEMATICA_COMPUTACIONAL-909E626D6BB0","sequence":2,"source":"MatematicaComputacional.pdf","source_key":"matematica_computacional","start_page":26,"end_page":50,"text_length":43184,"text_checksum":"36337e21ad729b4b631865a2e61afa5a2360798b1ccc71e450312e1c7f27eeb0","cache_file":"matematica_computacional\\MATEMATICA_COMPUTACIONAL-909E626D6BB0.txt"},{"id":"MATEMATICA_COMPUTACIONAL-6C77A8CB9BE6","sequence":3,"source":"MatematicaComputacional.pdf","source_key":"matematica_computacional","start_page":51,"end_page":75,"text_length":48772,"text_checksum":"58baad0b7f39aa9a2383ab632387d6e3d6175a6cb6f5544c6f774c43f3d98095","cache_file":"matematica_computacional\\MATEMATICA_COMPUTACIONAL-6C77A8CB9BE6.txt"},{"id":"MATEMATICA_COMPUTACIONAL-F7E79A727071","sequence":4,"source":"MatematicaComputacional.pdf","source_key":"matematica_computacional","start_page":76,"end_page":100,"text_length":44686,"text_checksum":"526c5f44157e9dd41d67271e296804d3f3ed923e7347b154938be60689bb7e9a","cache_file":"matematica_computacional\\MATEMATICA_COMPUTACIONAL-F7E79A727071.txt"},{"id":"MATEMATICA_COMPUTACIONAL-542A17C109AE","sequence":5,"source":"MatematicaComputacional.pdf","source_key":"matematica_computacional","start_page":101,"end_page":125,"text_length":43643,"text_checksum":"c35237eef872f298ebf75336be508d42baed19a3b1404d6ce3c4177c8f7aa716","cache_file":"matematica_computacional\\MATEMATICA_COMPUTACIONAL-542A17C109AE.txt"},{"id":"MATEMATICA_COMPUTACIONAL-5ABF7E583415","sequence":6,"source":"MatematicaComputacional.pdf","source_key":"matematica_computacional","start_page":126,"end_page":150,"text_length":41196,"text_checksum":"c51bfd843835247e963edd2f40e87780950799da1e2cc28f14fe89e62c8a48b1","cache_file":"matematica_computacional\\MATEMATICA_COMPUTACIONAL-5ABF7E583415.txt"},{"id":"MATEMATICA_COMPUTACIONAL-ADB8DA996932","sequence":7,"source":"MatematicaComputacional.pdf","source_key":"matematica_computacional","start_page":151,"end_page":175,"text_length":46017,"text_checksum":"a0f0b27a2d9f476f71511fcd259e376e67866529c45e5bfe4ae32971cf10125b","cache_file":"matematica_computacional\\MATEMATICA_COMPUTACIONAL-ADB8DA996932.txt"},{"id":"MATEMATICA_COMPUTACIONAL-78DFA175BA3E","sequence":8,"source":"MatematicaComputacional.pdf","source_key":"matematica_computacional","start_page":176,"end_page":192,"text_length":26953,"text_checksum":"99053c68dc1a4fd39c481323f6872c4aafe716b141d4b5760bda0b87178d278b","cache_file":"matematica_computacional\\MATEMATICA_COMPUTACIONAL-78DFA175BA3E.txt"}]},{"schema_version":"1.0","builder_version":"1.0.0","source":{"name":"portuguese_language_knowledge.pdf","key":"portuguese_language_knowledge","sha256":"54e55ce74fea4a06c317dd4011954357ce4af64d576e7aeac0d412071a04b3c4","type":"pdf"},"chunking":{"unit":"pages","size":25,"preserves_source_text":true,"summarizes":false,"cache_policy":"private_local"},"chunks":[{"id":"PORTUGUESE_LANGUAGE_KNOWLEDGE-6D6AF6C3B49F","sequence":1,"source":"portuguese_language_knowledge.pdf","source_key":"portuguese_language_knowledge","start_page":1,"end_page":25,"text_length":39870,"text_checksum":"35d2a1e9de227044da72bff4660605f5e0b08886322a90073c7d422bd018ac60","cache_file":"portuguese_language_knowledge\\PORTUGUESE_LANGUAGE_KNOWLEDGE-6D6AF6C3B49F.txt"},{"id":"PORTUGUESE_LANGUAGE_KNOWLEDGE-5FA2F5CB4ABB","sequence":2,"source":"portuguese_language_knowledge.pdf","source_key":"portuguese_language_knowledge","start_page":26,"end_page":50,"text_length":57872,"text_checksum":"e0324b769d58707a109bec67671c2bae4c4cbda04f0f32615363255efa185bc5","cache_file":"portuguese_language_knowledge\\PORTUGUESE_LANGUAGE_KNOWLEDGE-5FA2F5CB4ABB.txt"},{"id":"PORTUGUESE_LANGUAGE_KNOWLEDGE-707869DB28A4","sequence":3,"source":"portuguese_language_knowledge.pdf","source_key":"portuguese_language_knowledge","start_page":51,"end_page":75,"text_length":57372,"text_checksum":"49e143848dcdd551d1855d32563e0fa85d2fa190fd4b982b27074581389c52cb","cache_file":"portuguese_language_knowledge\\PORTUGUESE_LANGUAGE_KNOWLEDGE-707869DB28A4.txt"},{"id":"PORTUGUESE_LANGUAGE_KNOWLEDGE-5BA56CEA70AA","sequence":4,"source":"portuguese_language_knowledge.pdf","source_key":"portuguese_language_knowledge","start_page":76,"end_page":100,"text_length":58671,"text_checksum":"e1c8139b2f3b6fd0ff3a5652a1a9c5798baea956c7185dd47b90272139fec74d","cache_file":"portuguese_language_knowledge\\PORTUGUESE_LANGUAGE_KNOWLEDGE-5BA56CEA70AA.txt"},{"id":"PORTUGUESE_LANGUAGE_KNOWLEDGE-27DCC3509BC0","sequence":5,"source":"portuguese_language_knowledge.pdf","source_key":"portuguese_language_knowledge","start_page":101,"end_page":125,"text_length":52489,"text_checksum":"2e897d836578d812b89938cabf31f3850405d77f6d41bcd5c21e1e9ea3c1eaf7","cache_file":"portuguese_language_knowledge\\PORTUGUESE_LANGUAGE_KNOWLEDGE-27DCC3509BC0.txt"}]},{"schema_version":"1.0","builder_version":"1.0.0","source":{"name":"Raciocinio_Logico_e_Matematica_Para_Concursos_Cespe.pdf","key":"raciocinio_logico_matematica","sha256":"5ec0078c91ef0c4e16c2e70773bab0134d64c91f1299b68f46dd6d5421bc1987","type":"pdf"},"chunking":{"unit":"pages","size":25,"preserves_source_text":true,"summarizes":false,"cache_policy":"private_local"},"chunks":[{"id":"RACIOCINIO_LOGICO_MATEMATICA-826EB0C22532","sequence":1,"source":"Raciocinio_Logico_e_Matematica_Para_Concursos_Cespe.pdf","source_key":"raciocinio_logico_matematica","start_page":1,"end_page":25,"text_length":26311,"text_checksum":"4ea479cb4f4c2f13f803db45df745f13d8a09eda7824003653447ade8c31a851","cache_file":"raciocinio_logico_matematica\\RACIOCINIO_LOGICO_MATEMATICA-826EB0C22532.txt"},{"id":"RACIOCINIO_LOGICO_MATEMATICA-FB7052DBF395","sequence":2,"source":"Raciocinio_Logico_e_Matematica_Para_Concursos_Cespe.pdf","source_key":"raciocinio_logico_matematica","start_page":26,"end_page":50,"text_length":51932,"text_checksum":"6fb53b161f2ac719a7185db1e8461be7609607052e361966038bd05d1f9c348d","cache_file":"raciocinio_logico_matematica\\RACIOCINIO_LOGICO_MATEMATICA-FB7052DBF395.txt"},{"id":"RACIOCINIO_LOGICO_MATEMATICA-3238564A1668","sequence":3,"source":"Raciocinio_Logico_e_Matematica_Para_Concursos_Cespe.pdf","source_key":"raciocinio_logico_matematica","start_page":51,"end_page":75,"text_length":48244,"text_checksum":"d53e0b65375db5c78944e00afc8c7aca4c4d6b653953f639cf4990734f257bac","cache_file":"raciocinio_logico_matematica\\RACIOCINIO_LOGICO_MATEMATICA-3238564A1668.txt"},{"id":"RACIOCINIO_LOGICO_MATEMATICA-E68DD1EAB4E7","sequence":4,"source":"Raciocinio_Logico_e_Matematica_Para_Concursos_Cespe.pdf","source_key":"raciocinio_logico_matematica","start_page":76,"end_page":100,"text_length":51082,"text_checksum":"644a628867fe89321af5a2941afdee2cb3499d86a24476434a8f7c5f056b66e8","cache_file":"raciocinio_logico_matematica\\RACIOCINIO_LOGICO_MATEMATICA-E68DD1EAB4E7.txt"},{"id":"RACIOCINIO_LOGICO_MATEMATICA-26D11EF77264","sequence":5,"source":"Raciocinio_Logico_e_Matematica_Para_Concursos_Cespe.pdf","source_key":"raciocinio_logico_matematica","start_page":101,"end_page":125,"text_length":48708,"text_checksum":"e1b1fcd76e542125377f619cf0d2d2a9d08877cfc45ce7073a9b889c63b7260b","cache_file":"raciocinio_logico_matematica\\RACIOCINIO_LOGICO_MATEMATICA-26D11EF77264.txt"},{"id":"RACIOCINIO_LOGICO_MATEMATICA-E5DB95ED1BE3","sequence":6,"source":"Raciocinio_Logico_e_Matematica_Para_Concursos_Cespe.pdf","source_key":"raciocinio_logico_matematica","start_page":126,"end_page":150,"text_length":56183,"text_checksum":"f45003c9b538e45c74efd06c1869649b18480d8853d4664b90db00f1d93cb025","cache_file":"raciocinio_logico_matematica\\RACIOCINIO_LOGICO_MATEMATICA-E5DB95ED1BE3.txt"},{"id":"RACIOCINIO_LOGICO_MATEMATICA-852F470E8C4B","sequence":7,"source":"Raciocinio_Logico_e_Matematica_Para_Concursos_Cespe.pdf","source_key":"raciocinio_logico_matematica","start_page":151,"end_page":175,"text_length":61602,"text_checksum":"e782cc8b3647c00ed0bfe6247f3fb9693a0b9f99c7cd6b9ce4c4988cbdfeeb63","cache_file":"raciocinio_logico_matematica\\RACIOCINIO_LOGICO_MATEMATICA-852F470E8C4B.txt"},{"id":"RACIOCINIO_LOGICO_MATEMATICA-B90130B0337D","sequence":8,"source":"Raciocinio_Logico_e_Matematica_Para_Concursos_Cespe.pdf","source_key":"raciocinio_logico_matematica","start_page":176,"end_page":200,"text_length":64352,"text_checksum":"e9607e87fe2803bbded0ed1c1575a7b5a343b5bd35b8b25c079f2200439580bb","cache_file":"raciocinio_logico_matematica\\RACIOCINIO_LOGICO_MATEMATICA-B90130B0337D.txt"},{"id":"RACIOCINIO_LOGICO_MATEMATICA-8E1053DD2620","sequence":9,"source":"Raciocinio_Logico_e_Matematica_Para_Concursos_Cespe.pdf","source_key":"raciocinio_logico_matematica","start_page":201,"end_page":201,"text_length":42,"text_checksum":"6cd09d3b6ce59e377081009f983655fe2fa659600e21f968bb6dd40853899a5b","cache_file":"raciocinio_logico_matematica\\RACIOCINIO_LOGICO_MATEMATICA-8E1053DD2620.txt"}]},{"schema_version":"1.0","builder_version":"1.0.0","source":{"name":"Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf","key":"sapiens","sha256":"5e05b6919909e3ee77de3f91d3b32aedb1447f844971aec7f05a4d9c0f508eee","type":"pdf"},"chunking":{"unit":"pages","size":25,"preserves_source_text":true,"summarizes":false,"cache_policy":"private_local"},"chunks":[{"id":"SAPIENS-C0A5AE9C57B0","sequence":1,"source":"Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf","source_key":"sapiens","start_page":1,"end_page":25,"text_length":32145,"text_checksum":"b6c62eb7b7faaffe26d953d0e47657917fd83cd185b0fde9a2d6f21d87a76fe3","cache_file":"sapiens\\SAPIENS-C0A5AE9C57B0.txt"},{"id":"SAPIENS-3FEB0220045C","sequence":2,"source":"Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf","source_key":"sapiens","start_page":26,"end_page":50,"text_length":46594,"text_checksum":"17f3548a82fcb8f380908c555362ae7ef7368161cc24b44fb1b8d9a537868b92","cache_file":"sapiens\\SAPIENS-3FEB0220045C.txt"},{"id":"SAPIENS-EE694DAC02C4","sequence":3,"source":"Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf","source_key":"sapiens","start_page":51,"end_page":75,"text_length":48701,"text_checksum":"2128c2bbbbcff0bfa3cec5c6582ebc0897023c4201f27b083fc93e5f981c9452","cache_file":"sapiens\\SAPIENS-EE694DAC02C4.txt"},{"id":"SAPIENS-8DB2612155FC","sequence":4,"source":"Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf","source_key":"sapiens","start_page":76,"end_page":100,"text_length":45391,"text_checksum":"aa238b22484373635f37b0e55c7feef10e382cadf7bdc7b0ae9aafbcdc7c8c18","cache_file":"sapiens\\SAPIENS-8DB2612155FC.txt"},{"id":"SAPIENS-D00DADDBAFC8","sequence":5,"source":"Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf","source_key":"sapiens","start_page":101,"end_page":125,"text_length":46815,"text_checksum":"19f45aa0c4c8545318bd5840ee158c4225d840a1f6dd6728a03eaa062777b65e","cache_file":"sapiens\\SAPIENS-D00DADDBAFC8.txt"},{"id":"SAPIENS-F3B80B38E22F","sequence":6,"source":"Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf","source_key":"sapiens","start_page":126,"end_page":150,"text_length":47570,"text_checksum":"e4885615f1ec82b033aa7cf462b4559669c78348494f08fbc31006776d697aad","cache_file":"sapiens\\SAPIENS-F3B80B38E22F.txt"},{"id":"SAPIENS-C9A063D77C76","sequence":7,"source":"Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf","source_key":"sapiens","start_page":151,"end_page":175,"text_length":45732,"text_checksum":"4354f7ce09bdd2c20692ebe1e5296508caaf226be1dd99e52244c0b4fece2bf0","cache_file":"sapiens\\SAPIENS-C9A063D77C76.txt"},{"id":"SAPIENS-C706D47E57E9","sequence":8,"source":"Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf","source_key":"sapiens","start_page":176,"end_page":200,"text_length":40193,"text_checksum":"1e4ae5f3342082620f9df28db9e857d60205a4e32792534f66a870f0364c9ee8","cache_file":"sapiens\\SAPIENS-C706D47E57E9.txt"},{"id":"SAPIENS-A55B52FA07CF","sequence":9,"source":"Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf","source_key":"sapiens","start_page":201,"end_page":225,"text_length":48430,"text_checksum":"7c97c4876e308112d220a6f74c0527030fc4850ba766d5a1299b5d7144c94adf","cache_file":"sapiens\\SAPIENS-A55B52FA07CF.txt"},{"id":"SAPIENS-BAE9B341E493","sequence":10,"source":"Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf","source_key":"sapiens","start_page":226,"end_page":250,"text_length":44312,"text_checksum":"37affbeb381c906a2041cea97796cde237323d1405b615b4590452bc2fa7788c","cache_file":"sapiens\\SAPIENS-BAE9B341E493.txt"},{"id":"SAPIENS-06566B4CD3DD","sequence":11,"source":"Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf","source_key":"sapiens","start_page":251,"end_page":275,"text_length":40922,"text_checksum":"f0fc28b6a4ab514910df9fc2993a1a02d334e871c7a7fdca3d3630e08ad69e26","cache_file":"sapiens\\SAPIENS-06566B4CD3DD.txt"},{"id":"SAPIENS-75591DF9D815","sequence":12,"source":"Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf","source_key":"sapiens","start_page":276,"end_page":300,"text_length":46854,"text_checksum":"a4c1e33301d3980f5328617dfacf0771c920542f4d3a8296dceffa161b60fde7","cache_file":"sapiens\\SAPIENS-75591DF9D815.txt"},{"id":"SAPIENS-C851DE33B9C3","sequence":13,"source":"Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf","source_key":"sapiens","start_page":301,"end_page":325,"text_length":48147,"text_checksum":"5df4e6521c735412cdfc870d85d098acf23188b8fac6bb90e16a1d0d8451ae1f","cache_file":"sapiens\\SAPIENS-C851DE33B9C3.txt"},{"id":"SAPIENS-2195FD7E3B43","sequence":14,"source":"Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf","source_key":"sapiens","start_page":326,"end_page":350,"text_length":47603,"text_checksum":"89ff0b86fe9713f3e6c6ac6daa33560333377bab5a2eb243f7a15be3e348e8a0","cache_file":"sapiens\\SAPIENS-2195FD7E3B43.txt"},{"id":"SAPIENS-F8B99E91DEC0","sequence":15,"source":"Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf","source_key":"sapiens","start_page":351,"end_page":375,"text_length":46093,"text_checksum":"dc908b13ec2776287137411136bdaa18a55f9725cd0e05d45e2bd2f28c4bf116","cache_file":"sapiens\\SAPIENS-F8B99E91DEC0.txt"},{"id":"SAPIENS-3612835835EE","sequence":16,"source":"Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf","source_key":"sapiens","start_page":376,"end_page":400,"text_length":46497,"text_checksum":"b210c8885c881e37b8eba331fdab67f6b30a79a07aa5a7c38bd9d197f4153771","cache_file":"sapiens\\SAPIENS-3612835835EE.txt"},{"id":"SAPIENS-FF08F77664B1","sequence":17,"source":"Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf","source_key":"sapiens","start_page":401,"end_page":425,"text_length":48111,"text_checksum":"814f2d7b6af15c6b098e47636d9ae99a20bf83bbf6d36a94e41b4799fa0eba81","cache_file":"sapiens\\SAPIENS-FF08F77664B1.txt"},{"id":"SAPIENS-DA9F3E981D79","sequence":18,"source":"Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf","source_key":"sapiens","start_page":426,"end_page":450,"text_length":49681,"text_checksum":"de15a10f1dd8889f5cdb79ea02b041c6dc83a9a66fbd53ce79c445ad8adbcffc","cache_file":"sapiens\\SAPIENS-DA9F3E981D79.txt"},{"id":"SAPIENS-A56A1ED270E5","sequence":19,"source":"Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf","source_key":"sapiens","start_page":451,"end_page":475,"text_length":46600,"text_checksum":"fa69f48311e4038eab0c50b1376b3c4547354a6fa6a6bf2c3bbeb2e696baac82","cache_file":"sapiens\\SAPIENS-A56A1ED270E5.txt"},{"id":"SAPIENS-47ADA8FA160B","sequence":20,"source":"Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf","source_key":"sapiens","start_page":476,"end_page":500,"text_length":51383,"text_checksum":"a924c6715e4916a3b90e6f9e5cb5e9079f5a5612280e011eabe1e7f831f53fba","cache_file":"sapiens\\SAPIENS-47ADA8FA160B.txt"},{"id":"SAPIENS-C68E9539629D","sequence":21,"source":"Sapiens uma Breve História da Humanidade - Yuval Noah Harari.pdf","source_key":"sapiens","start_page":501,"end_page":506,"text_length":4256,"text_checksum":"7067a5f2f3a9768e8be147788481f7fac17584eb39d86d464d71a982d0c62323","cache_file":"sapiens\\SAPIENS-C68E9539629D.txt"}]}]''')
library_runtime.EMBEDDED_LIBRARY_INDEXES = EMBEDDED_LIBRARY_INDEXES

class Default(WorkerEntrypoint):
    async def fetch(self, request):
        method = str(request.method or "GET").upper()
        parsed = urlparse(str(request.url))
        path = parsed.path.rstrip("/") or "/"

        # Normaliza o prefixo da rota do domínio oficial.
        if path == "/aigar/api":
            path = "/"
        elif path.startswith("/aigar/api/"):
            path = path[len("/aigar/api"):]

        origin = _request_origin(request)

        if method == "OPTIONS":
            return Response(None, status=204, headers=cors_headers(origin))

        if method == "GET" and path == "/health":
            r2_ready = binding(self.env, R2_BINDING) is not None
            d1_ready = binding(self.env, D1_BINDING) is not None
            storage_ready = r2_ready and d1_ready
            return make_response({
                "ok": True,
                "service": "aigar-api",
                "runtime": "AIGAR",
                "version": "0.8.0-adaptive-cloudflare",
                "status": "online",
                "backend": "python_workers",
                "checks": {
                    "api": "ok",
                    "r2_binding": r2_ready,
                    "d1_binding": d1_ready,
                    "persistent_storage_configured": storage_ready,
                },
                "features": {
                    "language": True,
                    "hybrid_library_search": True,
                    "session_memory": True,
                    "persistent_library_upload": True,
                    "persistent_storage_ready": storage_ready,
                    "adaptive_interaction_profiles": True,
                    "adaptive_plan_revision": True,
                    "cognitive_core_preloaded": True,
                    "speaker_addressee_context_cache": True,
                    "feedback_api": True,
                    "memory_lab_module": True,
                    "admin_useful_logs": True,
                },
            }, origin=origin)

        if method == "GET" and path == "/memory/status":
            try:
                status = await MEMORY_LAB.initialize()
                return make_response({"ok": True, "memory_lab": status}, status=200, origin=origin)
            except Exception as exc:
                return make_response({"ok": False, "memory_lab": {"ready": False, "mode": "error", "error": str(exc)[:500]}}, status=200, origin=origin)

        if method == "GET" and path == "/texto-matriz/boot":
            try:
                matrix = await boot_text_matrix()
                return make_response({"ok": True, "text_matrix": matrix}, status=200, origin=origin)
            except Exception as exc:
                return make_response({"ok": False, "text_matrix": {"ready": False, "loaded": 0, "total": len(TEXT_MATRIX_FILES), "error": str(exc)[:500]}}, status=200, origin=origin)

        if method == "GET" and path == "/library/boot":
            try:
                boot = await boot_library()
                return make_response({
                    "ok": True,
                    "library": boot,
                }, status=200 if boot.get("loaded", 0) > 0 else 503, origin=origin)
            except Exception as exc:
                return make_response({
                    "ok": False,
                    "library": {
                        "ready": False,
                        "libraries": [],
                        "loaded": 0,
                        "total": 0,
                        "mode": "error",
                    },
                    "message": str(exc)[:1000],
                }, status=500, origin=origin)

        if method == "POST" and path == "/perguntar":
            body = await _json_body(request)
            status, data = await handle_ask(body, self.env)
            return make_response(data, status=status, origin=origin)

        if method == "POST" and path == "/feedback":
            body = await _json_body(request)
            db = binding(self.env, D1_BINDING)
            if not db:
                return make_response({"ok": False, "status": "storage_not_configured", "message": "O banco de feedback ainda não está configurado."}, status=503, origin=origin)
            if not await adaptive_schema_ready(db):
                return make_response({"ok": False, "status": "adaptive_schema_not_ready", "message": "A migração da camada adaptativa ainda não foi aplicada ao D1."}, status=503, origin=origin)
            category = str(body.get("category") or "other")
            rating = str(body.get("rating") or "incomplete")
            interaction_id = _clip(body.get("interaction_id"), 80)
            comment = _clip(body.get("comment"), 2000)
            if category not in FEEDBACK_CATEGORIES or rating not in FEEDBACK_RATINGS:
                return make_response({"ok": False, "status": "invalid_feedback", "message": "Categoria ou avaliação inválida."}, status=400, origin=origin)
            if interaction_id:
                exists = await db.prepare("SELECT id FROM adaptive_interactions WHERE id = ? LIMIT 1").bind(interaction_id).first()
                if not exists:
                    return make_response({"ok": False, "status": "interaction_not_found", "message": "A interação não está registrada no banco. Tente novamente quando a persistência estiver disponível."}, status=409, origin=origin)
            feedback_id = str(uuid.uuid4())
            try:
                await db.prepare(
                    """INSERT INTO adaptive_feedback
                       (id, interaction_id, category, rating, comment, status, created_at)
                       VALUES (?, ?, ?, ?, ?, 'pending', ?)"""
                ).bind(feedback_id, interaction_id, category, rating, comment, _utc_now()).run()
            except Exception as exc:
                return make_response({"ok": False, "status": "feedback_write_failed", "message": str(exc)[:300]}, status=500, origin=origin)
            return make_response({"ok": True, "feedback_id": feedback_id, "status": "pending"}, status=201, origin=origin)

        if method == "POST" and path == "/auth/login":
            body = await _json_body(request)
            try:
                status, data = await medunity_admin_login(body)
                return make_response(data, status=status, origin=origin)
            except Exception as exc:
                return make_response({
                    "detail": "Não foi possível validar as credenciais no MedUnity.",
                    "error": str(exc)[:500],
                }, status=502, origin=origin)

        if path == "/auth/me" and method == "GET":
            status, data = await medunity_me(request)
            return make_response(data, status=status, origin=origin)

        if path.startswith("/admin/"):
            usuario, auth_status, auth_data = await require_admin(request)
            if not usuario:
                return make_response(auth_data, status=auth_status, origin=origin)

            if path == "/admin/storage" and method == "GET":
                storage = await storage_status(self.env)
                return make_response({
                    "ok": True,
                    "ready": storage["ready"],
                    "storage": storage,
                }, status=200, origin=origin)

            if path == "/admin/documents" and method == "GET":
                status, data = await admin_documents(self.env)
                return make_response(data, status=status, origin=origin)

            if path == "/admin/upload" and method == "POST":
                status, data = await admin_upload(request, self.env, usuario)
                return make_response(data, status=status, origin=origin)

            # Administração do feedback e do conjunto de avaliação: todas as rotas
            # abaixo estão protegidas por require_admin() no servidor.
            db = binding(self.env, D1_BINDING)
            if path.startswith("/admin/feedback") or path.startswith("/admin/useful-logs"):
                if not db:
                    return make_response({"ok": False, "status": "storage_not_configured", "message": "O banco D1 não está configurado."}, status=503, origin=origin)
                if not await adaptive_schema_ready(db):
                    return make_response({"ok": False, "status": "adaptive_schema_not_ready", "message": "A migração da camada adaptativa ainda não foi aplicada ao D1."}, status=503, origin=origin)

            if path == "/admin/feedback" and method == "GET":
                try:
                    rows = (await db.prepare(
                        """SELECT id, interaction_id, category, rating, comment, status, created_at
                           FROM adaptive_feedback ORDER BY created_at DESC LIMIT 100"""
                    ).all()).results
                    return make_response({"ok": True, "items": [dict(row) for row in rows]}, origin=origin)
                except Exception as exc:
                    return make_response({"ok": False, "status": "feedback_query_failed", "message": str(exc)[:300]}, status=500, origin=origin)

            if path == "/admin/feedback/metrics" and method == "GET":
                try:
                    totals = await db.prepare(
                        "SELECT COUNT(*) AS total FROM adaptive_feedback"
                    ).first()
                    by_status = (await db.prepare(
                        "SELECT status, COUNT(*) AS count FROM adaptive_feedback GROUP BY status"
                    ).all()).results
                    by_category = (await db.prepare(
                        "SELECT category, COUNT(*) AS count FROM adaptive_feedback GROUP BY category"
                    ).all()).results
                    by_rating = (await db.prepare(
                        "SELECT rating, COUNT(*) AS count FROM adaptive_feedback GROUP BY rating"
                    ).all()).results
                    decisions = (await db.prepare(
                        "SELECT decision, COUNT(*) AS count FROM adaptive_feedback_reviews GROUP BY decision"
                    ).all()).results
                    return make_response({"ok": True, "metrics": {
                        "total_feedback": int(totals.total if totals else 0),
                        "by_status": [dict(row) for row in by_status],
                        "by_category": [dict(row) for row in by_category],
                        "by_rating": [dict(row) for row in by_rating],
                        "review_decisions": [dict(row) for row in decisions],
                    }}, origin=origin)
                except Exception as exc:
                    return make_response({"ok": False, "status": "metrics_query_failed", "message": str(exc)[:300]}, status=500, origin=origin)

            if path == "/admin/useful-logs" and method == "POST":
                body = await _json_body(request)
                purpose = _clip(body.get("purpose"), 500)
                session_id = _clip(body.get("session_id"), 128) or ""
                turn_id = _clip(body.get("turn_id"), 100)
                interaction_id = _clip(body.get("interaction_id"), 80)
                try:
                    snapshot = _safe_useful_snapshot(body.get("minimal_snapshot") or body.get("snapshot") or {})
                except ValueError as exc:
                    return make_response({"ok": False, "status": "snapshot_too_large", "message": str(exc)}, status=400, origin=origin)
                if not purpose or len(purpose) < 3:
                    return make_response({"ok": False, "status": "invalid_purpose", "message": "Informe a finalidade do registro."}, status=400, origin=origin)
                if interaction_id:
                    exists = await db.prepare("SELECT id FROM adaptive_interactions WHERE id = ? LIMIT 1").bind(interaction_id).first()
                    if not exists:
                        return make_response({"ok": False, "status": "interaction_not_found", "message": "Interação não encontrada."}, status=404, origin=origin)
                    snapshot["interaction_id"] = interaction_id
                log_id = str(uuid.uuid4())
                session_hash = hashlib.sha256(session_id.encode("utf-8")).hexdigest()[:32] if session_id else ""
                actor_id = str(usuario.get("id") or usuario.get("usuario_id") or usuario.get("email") or "admin")[:200]
                try:
                    await db.prepare(
                        """INSERT INTO adaptive_useful_interaction_logs
                           (id, session_hash, turn_id, interaction_id, purpose, minimal_snapshot_json, created_by, created_at)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
                    ).bind(log_id, session_hash, turn_id, interaction_id, purpose,
                           json.dumps(snapshot, ensure_ascii=False), actor_id, _utc_now()).run()
                    await _audit_admin_action(db, actor_id, "create_useful_interaction_log", "useful_interaction_log", log_id, {"purpose": purpose, "interaction_id": interaction_id})
                    return make_response({"ok": True, "log_id": log_id, "status": "recorded"}, status=201, origin=origin)
                except Exception as exc:
                    return make_response({"ok": False, "status": "useful_log_write_failed", "message": str(exc)[:300]}, status=500, origin=origin)

            if path == "/admin/useful-logs" and method == "GET":
                try:
                    rows = (await db.prepare(
                        """SELECT id, session_hash, turn_id, interaction_id, purpose,
                                  minimal_snapshot_json, created_by, created_at
                           FROM adaptive_useful_interaction_logs ORDER BY created_at DESC LIMIT 100"""
                    ).all()).results
                    items = []
                    for row in rows:
                        item = dict(row)
                        try:
                            item["minimal_snapshot"] = json.loads(item.pop("minimal_snapshot_json") or "{}")
                        except Exception:
                            item["minimal_snapshot"] = {}
                        items.append(item)
                    return make_response({"ok": True, "items": items}, origin=origin)
                except Exception as exc:
                    return make_response({"ok": False, "status": "useful_logs_query_failed", "message": str(exc)[:300]}, status=500, origin=origin)

            review_match = re.fullmatch(r"/admin/feedback/([A-Za-z0-9_-]+)/review", path)
            if review_match and method == "POST":
                body = await _json_body(request)
                feedback_id = review_match.group(1)
                root_cause = str(body.get("root_cause") or "other")
                decision = str(body.get("decision") or "inconclusive")
                notes = _clip(body.get("notes"), 4000)
                if root_cause not in FEEDBACK_ROOT_CAUSES or decision not in FEEDBACK_DECISIONS:
                    return make_response({"ok": False, "status": "invalid_review", "message": "Causa-raiz ou decisão de revisão inválida."}, status=400, origin=origin)
                feedback_row = await db.prepare("SELECT id FROM adaptive_feedback WHERE id = ? LIMIT 1").bind(feedback_id).first()
                if not feedback_row:
                    return make_response({"ok": False, "status": "feedback_not_found", "message": "Feedback não encontrado."}, status=404, origin=origin)
                review_id = str(uuid.uuid4())
                actor_id = str(usuario.get("id") or usuario.get("usuario_id") or usuario.get("email") or "admin")[:200]
                now = _utc_now()
                try:
                    await db.prepare(
                        """INSERT INTO adaptive_feedback_reviews
                           (id, feedback_id, reviewer_id, root_cause, decision, notes, reviewed_at)
                           VALUES (?, ?, ?, ?, ?, ?, ?)"""
                    ).bind(review_id, feedback_id, actor_id, root_cause, decision, notes, now).run()
                    await db.prepare("UPDATE adaptive_feedback SET status = 'reviewed' WHERE id = ?").bind(feedback_id).run()
                    await _audit_admin_action(db, actor_id, "review_feedback", "feedback", feedback_id, {"decision": decision, "root_cause": root_cause})
                    return make_response({"ok": True, "review_id": review_id, "status": "reviewed"}, status=201, origin=origin)
                except Exception as exc:
                    return make_response({"ok": False, "status": "review_write_failed", "message": str(exc)[:300]}, status=500, origin=origin)

            evaluation_match = re.fullmatch(r"/admin/feedback/([A-Za-z0-9_-]+)/evaluation-case", path)
            if evaluation_match and method == "POST":
                body = await _json_body(request)
                feedback_id = evaluation_match.group(1)
                expected_behavior = _clip(body.get("expected_behavior"), 4000)
                if not expected_behavior or len(expected_behavior) < 5:
                    return make_response({"ok": False, "status": "invalid_expected_behavior", "message": "Descreva o comportamento esperado (mínimo de 5 caracteres)."}, status=400, origin=origin)
                feedback_row = await db.prepare("SELECT id, interaction_id FROM adaptive_feedback WHERE id = ? LIMIT 1").bind(feedback_id).first()
                if not feedback_row:
                    return make_response({"ok": False, "status": "feedback_not_found", "message": "Feedback não encontrado."}, status=404, origin=origin)
                review_row = await db.prepare("SELECT id FROM adaptive_feedback_reviews WHERE feedback_id = ? ORDER BY reviewed_at DESC LIMIT 1").bind(feedback_id).first()
                if not review_row:
                    return make_response({"ok": False, "status": "review_required", "message": "Revise o feedback antes de criar um caso de avaliação."}, status=409, origin=origin)
                snapshot = _safe_useful_snapshot(body.get("input_snapshot") or {})
                if not snapshot and feedback_row.interaction_id:
                    interaction = await db.prepare("SELECT minimal_snapshot_json FROM adaptive_interactions WHERE id = ? LIMIT 1").bind(feedback_row.interaction_id).first()
                    if interaction:
                        try:
                            snapshot = json.loads(interaction.minimal_snapshot_json or "{}")
                        except Exception:
                            snapshot = {}
                case_id = str(uuid.uuid4())
                actor_id = str(usuario.get("id") or usuario.get("usuario_id") or usuario.get("email") or "admin")[:200]
                try:
                    await db.prepare(
                        """INSERT INTO adaptive_evaluation_cases
                           (id, review_id, input_snapshot_json, expected_behavior, training_eligible, dataset_version, created_at)
                           VALUES (?, ?, ?, ?, 0, ?, ?)"""
                    ).bind(case_id, review_row.id, json.dumps(snapshot, ensure_ascii=False), expected_behavior,
                           _clip(body.get("dataset_version"), 100), _utc_now()).run()
                    await _audit_admin_action(db, actor_id, "create_evaluation_case", "evaluation_case", case_id, {"training_eligible": False})
                    return make_response({"ok": True, "evaluation_case_id": case_id, "training_eligible": False, "status": "created"}, status=201, origin=origin)
                except Exception as exc:
                    return make_response({"ok": False, "status": "evaluation_case_write_failed", "message": str(exc)[:300]}, status=500, origin=origin)

            detail_match = re.fullmatch(r"/admin/feedback/([A-Za-z0-9_-]+)", path)
            if detail_match and method == "GET":
                feedback_id = detail_match.group(1)
                row = await db.prepare(
                    "SELECT id, interaction_id, category, rating, comment, status, created_at FROM adaptive_feedback WHERE id = ? LIMIT 1"
                ).bind(feedback_id).first()
                if not row:
                    return make_response({"ok": False, "status": "feedback_not_found"}, status=404, origin=origin)
                reviews = (await db.prepare(
                    "SELECT id, reviewer_id, root_cause, decision, notes, reviewed_at FROM adaptive_feedback_reviews WHERE feedback_id = ? ORDER BY reviewed_at DESC"
                ).bind(feedback_id).all()).results
                return make_response({"ok": True, "feedback": dict(row), "reviews": [dict(item) for item in reviews]}, origin=origin)

            return make_response({
                "ok": False,
                "status": "not_found",
                "message": "Endpoint administrativo não encontrado.",
            }, status=404, origin=origin)

        return make_response({
            "ok": False,
            "status": "not_found",
            "message": "Endpoint não encontrado.",
            "path": path,
        }, status=404, origin=origin)
