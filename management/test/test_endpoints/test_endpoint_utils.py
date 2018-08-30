from management_api.endpoints.endpoint_utils import create_endpoint, delete_endpoint, \
    create_url_to_service, validate_params
from management_api.config import PLATFORM_DOMAIN
from kubernetes.client.rest import ApiException
import falcon
import pytest
from unittest.mock import Mock


@pytest.mark.parametrize("raise_error", [(False), (True)])
def test_create_endpoint(get_url_to_service_endpoint_utils, custom_client_mock_endpoint_utils,
                         raise_error):
    ing_ip_mock, ing_ip_mock_return_values = get_url_to_service_endpoint_utils
    create_custom_client_mock, custom_client = custom_client_mock_endpoint_utils
    if raise_error:
        with pytest.raises(falcon.HTTPBadRequest):
            custom_client.create_namespaced_custom_object.side_effect = ApiException()
            create_endpoint(parameters={'endpointName': "test"}, namespace="test")

    else:
        create_endpoint(parameters={'endpointName': "test"}, namespace="test")
        ing_ip_mock.assert_called_once()
    custom_client.create_namespaced_custom_object.assert_called_once()
    create_custom_client_mock.assert_called_once()


@pytest.mark.parametrize("raise_error", [(False), (True)])
def test_delete_endpoint(custom_client_mock_endpoint_utils, get_url_to_service_endpoint_utils,
                         raise_error):
    ing_ip_mock, ing_ip_mock_return_values = get_url_to_service_endpoint_utils
    create_custom_client_mock, custom_client = custom_client_mock_endpoint_utils

    if raise_error:
        with pytest.raises(falcon.HTTPBadRequest):
            custom_client.delete_namespaced_custom_object.side_effect = ApiException()
            delete_endpoint(parameters={'endpointName': 'test'}, namespace="test")
    else:
        delete_endpoint(parameters={'endpointName': 'test'}, namespace="test")

        ing_ip_mock.assert_called_once()
    custom_client.delete_namespaced_custom_object.assert_called_once()
    create_custom_client_mock.assert_called_once()


def test_create_url_to_service(mocker):
    api_client = Mock()
    create_custom_client_mock = mocker.patch('management_api.endpoints.endpoint_utils.'
                                             'get_k8s_api_client')
    create_custom_client_mock.return_value = api_client
    mock_return_value = ['127.0.0.1', 443]
    external_address_mock = mocker.patch('management_api.endpoints.endpoint_utils.'
                                         'get_ingress_external_ip')
    external_address_mock.return_value = mock_return_value
    external_address = "{}:{}".format(mock_return_value[0], mock_return_value[1])
    expected_output = {'address': external_address, 'opts': "t_end-t_ns.{}".format(PLATFORM_DOMAIN)}
    output = create_url_to_service(endpoint_name='t_end', namespace="t_ns")
    assert expected_output == output


@pytest.mark.parametrize("raise_error, params",
                         [(True, {'modelVersion': 3, 'replicas': 3, 'subjectName': 'test_w'}),
                          (False, {'modelVersion': 3, 'replicas': 3, 'subjectName': 'test-g'}),
                          (True, {'modelVersion': 'str', 'replicas': 3, 'subjectName': 'test_w'}),
                          (True, {'modelVersion': 'str', 'replicas': 'tet',
                                  'subjectName': 'test_w'}),
                          (True, {'modelVersion': 3, 'replicas': 'tet', 'subjectName': 'test_w'})])
def test_validate_params(raise_error, params):
    if raise_error:
        with pytest.raises(falcon.HTTPBadRequest):
            validate_params(params=params)
    else:
        validate_params(params=params)
