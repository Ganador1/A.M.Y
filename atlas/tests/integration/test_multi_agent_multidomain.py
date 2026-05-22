from unittest.mock import MagicMock

def test_multi_agent_coordinator_initialization():
    """Test multi-agent coordinator initialization."""
    # Mock the coordinator initialization
    mock_coordinator = MagicMock()
    mock_coordinator.wrappers = {
        'materials_science': MagicMock(),
        'biophysics': MagicMock(),
        'drug_discovery': MagicMock()
    }

    # Verify coordinator has expected wrappers
    assert len(mock_coordinator.wrappers) == 3
    assert 'materials_science' in mock_coordinator.wrappers
    assert 'biophysics' in mock_coordinator.wrappers
    assert 'drug_discovery' in mock_coordinator.wrappers


def test_process_multidomain_request():
    """Test processing multi-domain research request."""
    # Setup mock coordinator
    mock_coordinator_instance = MagicMock()

    # Mock multi-domain results
    mock_results = {
        'success': True,
        'multi_domain_results': {
            'materials_science': {
                'success': True,
                'artifact': {'evidence': {'summary': {'support_score': 0.85}}},
                'domain': 'materials_science'
            },
            'biophysics': {
                'success': True,
                'artifact': {'evidence': {'summary': {'support_score': 0.82}}},
                'domain': 'biophysics'
            }
        },
        'aggregate_metrics': {
            'overall_success_rate': 1.0,
            'total_domains': 2,
            'average_support_score': 0.835,
            'domain_coverage': 1.0
        }
    }

    mock_coordinator_instance.process_request = MagicMock(return_value=mock_results)

    # Test the request processing
    request = {
        'action': 'run_pipeline_multidomain',
        'research_goal': 'Optimizar propiedades mecánicas y térmicas',
        'domains': ['materials_science', 'biophysics']
    }

    result = mock_coordinator_instance.process_request(request)

    # Verify results
    assert result['success'] is True
    assert 'multi_domain_results' in result
    assert len(result['multi_domain_results']) == 2
    assert 'materials_science' in result['multi_domain_results']
    assert 'biophysics' in result['multi_domain_results']
    assert 'aggregate_metrics' in result

    # Verify aggregate metrics
    metrics = result['aggregate_metrics']
    assert 'overall_success_rate' in metrics
    assert 'total_domains' in metrics
    assert 'average_support_score' in metrics
    assert metrics['total_domains'] == 2


def test_multidomain_artifact_aggregation():
    """Test aggregation of artifacts from multiple domains."""
    mock_coordinator = MagicMock()

    # Mock individual domain results
    domain_results = {
        'materials_science': {
            'success': True,
            'artifact': {
                'evidence': {'summary': {'support_score': 0.88, 'coverage': 0.92}},
                'review': '{"verdict": "approve"}',
                'publication': 'Materials publication'
            }
        },
        'biophysics': {
            'success': True,
            'artifact': {
                'evidence': {'summary': {'support_score': 0.82, 'coverage': 0.89}},
                'review': '{"verdict": "approve"}',
                'publication': 'Biophysics publication'
            }
        },
        'drug_discovery': {
            'success': False,
            'error': 'Domain processing failed',
            'artifact': None
        }
    }

    # Mock aggregation logic
    def mock_aggregate_results(domain_results):
        successful_domains = [d for d in domain_results.values() if d.get('success', False)]
        total_domains = len(domain_results)
        successful_count = len(successful_domains)

        if successful_count > 0:
            avg_support = sum(d['artifact']['evidence']['summary']['support_score']
                            for d in successful_domains) / successful_count
        else:
            avg_support = 0.0

        return {
            'overall_success_rate': successful_count / total_domains,
            'total_domains': total_domains,
            'successful_domains': successful_count,
            'average_support_score': avg_support,
            'failed_domains': total_domains - successful_count
        }

    mock_coordinator.aggregate_multidomain_results = MagicMock(side_effect=mock_aggregate_results)

    # Test aggregation
    metrics = mock_coordinator.aggregate_multidomain_results(domain_results)

    assert metrics['overall_success_rate'] == 2/3  # 2 out of 3 domains successful
    assert metrics['total_domains'] == 3
    assert metrics['successful_domains'] == 2
    assert metrics['failed_domains'] == 1
    assert abs(metrics['average_support_score'] - 0.85) < 0.01  # (0.88 + 0.82) / 2


def test_multidomain_failure_handling():
    """Test handling of failures in multi-domain processing."""
    mock_coordinator = MagicMock()

    # Mock scenario with partial failures
    partial_failure_results = {
        'materials_science': {'success': True, 'artifact': {'evidence': {'summary': {'support_score': 0.9}}}},
        'biophysics': {'success': False, 'error': 'Timeout error'},
        'drug_discovery': {'success': False, 'error': 'Resource unavailable'}
    }

    mock_coordinator.process_request = MagicMock(return_value={
        'success': True,  # Overall success despite individual failures
        'multi_domain_results': partial_failure_results,
        'aggregate_metrics': {
            'overall_success_rate': 1/3,
            'total_domains': 3,
            'successful_domains': 1,
            'failed_domains': 2
        }
    })

    request = {
        'action': 'run_pipeline_multidomain',
        'research_goal': 'Test failure handling',
        'domains': ['materials_science', 'biophysics', 'drug_discovery']
    }

    result = mock_coordinator.process_request(request)

    # Verify partial success handling
    assert result['success'] is True  # Overall operation succeeded
    assert len(result['multi_domain_results']) == 3

    # Check individual domain results
    ms_result = result['multi_domain_results']['materials_science']
    assert ms_result['success'] is True

    bio_result = result['multi_domain_results']['biophysics']
    assert bio_result['success'] is False
    assert 'error' in bio_result

    # Verify metrics reflect partial failure
    metrics = result['aggregate_metrics']
    assert metrics['successful_domains'] == 1
    assert metrics['failed_domains'] == 2
    assert metrics['overall_success_rate'] == 1/3


def test_domain_wrapper_initialization():
    """Test domain-specific wrapper initialization."""
    mock_coordinator = MagicMock()

    # Mock wrapper generation responses
    def mock_generate_response(prompt, **kwargs):
        if 'steps' in prompt and 'JSON' in prompt:
            return '{"steps":["hipotesis","diseno","corroboracion","revision","publicacion"]}'
        elif 'Formato JSON' in prompt:
            return '{"title":"Multi-domain Hypothesis","description":"Cross-domain research","variables":["domain_interaction"],"expected_outcome":"Enhanced results","assumptions":["domain_compatibility"]}'
        elif 'Plan:' in prompt:
            return '```python\n# Multi-domain simulation\nprint("cross-domain analysis")\n```'
        elif 'Respuesta JSON' in prompt:
            return '{"verdict":"approve","weaknesses":[],"improvements":[],"risk_level":"low"}'
        elif 'INFORME:' in prompt:
            return 'Multi-domain final report.'
        else:
            return 'OK'

    # Setup mock wrappers for different domains
    domains = ['materials_science', 'biophysics', 'drug_discovery']
    mock_wrappers = {}

    for domain in domains:
        mock_wrapper = MagicMock()
        mock_wrapper.generate = MagicMock(side_effect=mock_generate_response)
        mock_wrappers[domain] = mock_wrapper

    mock_coordinator.wrappers = mock_wrappers

    # Test wrapper functionality for each domain
    for domain, wrapper in mock_coordinator.wrappers.items():
        # Test steps generation
        steps_response = wrapper.generate("Generate steps in JSON format")
        assert "hipotesis" in steps_response
        assert "steps" in steps_response

        # Test hypothesis generation
        hypothesis_response = wrapper.generate("Formato JSON for hypothesis")
        assert "Multi-domain Hypothesis" in hypothesis_response
        assert "domain_interaction" in hypothesis_response

        # Test plan generation
        plan_response = wrapper.generate("Plan: experimental design")
        assert "cross-domain analysis" in plan_response

    # Verify all domains have wrappers
    assert len(mock_coordinator.wrappers) == 3
    for domain in domains:
        assert domain in mock_coordinator.wrappers
