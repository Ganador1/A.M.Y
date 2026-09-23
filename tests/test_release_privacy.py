from scripts.release.privacy import findings, sanitize
from scripts.release.translate_manuals import mask, response_text


def test_private_identifiers_and_machine_paths_become_public_derivatives():
    text, changes = sanitize('Example Person /home/amy/work /workspace/tools', ['Example Person'])
    assert text == 'Ganador1 /home/amy/work /workspace/tools'
    assert not findings(text, ['Example Person'])
    assert changes['private_identifier'] == 1


def test_credentials_redacted_but_task_identifiers_survive():
    fake = 'sk-' + 'x' * 30
    task = 'task-' + 'a' * 32
    text, _ = sanitize(fake + ' ' + task, [])
    assert fake not in text and task in text
    assert findings(fake, []) == ['credential_pattern']


def test_container_user_and_ci_paths_keep_their_runtime_meaning():
    text = 'COPY /root/.local /home/axiom/.local\nPATH=/home/axiom/.local/bin\n/home/runner/work'
    assert sanitize(text, [])[0] == text
    assert sanitize('/home/amy/project', [])[0] == '/home/amy/project'


def test_translation_rejects_lost_literals_and_truncation():
    part, values = mask('Resultado `x=42` y valor 17. Texto suficientemente largo.')
    assert values == ['`x=42`', '17']
    assert response_text({'message': {'content': part}}, part)
    assert response_text({'message': {'content': part.replace('@@KEEP000000@@', '')}}, part) is None
    assert response_text({'message': {'content': part}, 'done_reason': 'length'}, part) is None
    assert response_text({'message': {'content': '{"text": "broken'}}, part) is None
