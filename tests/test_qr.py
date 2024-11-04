from idr.document.qr_codes import qr_code_to_dict, validate_qr_code


def test_qr_code():
    qr_code_string = "A:509104720*B:508453488*C:PT*D:NC*E:N*F:20240319*G:NC 2024A4/1*H:JJJRJ85C-1*I1:PT*I7:6390.21*I8:1469.75*N:1469.75*O:7859.96*Q:PqIU*R:0006"
    qr_code_dict = {
        "A": "509104720",
        "B": "508453488",
        "C": "PT",
        "D": "NC",
        "E": "N",
        "F": "20240319",
        "G": "NC 2024A4/1",
        "H": "JJJRJ85C-1",
        "I1": "PT",
        "I7": "6390.21",
        "I8": "1469.75",
        "N": "1469.75",
        "O": "7859.96",
        "Q": "PqIU",
        "R": "0006",
    }
    result = qr_code_to_dict(qr_code_string)
    assert validate_qr_code(qr_code_string)
    assert result == qr_code_dict
    assert not validate_qr_code("valvaefmearkofea")
    # remove required field
    assert not validate_qr_code(qr_code_string[12:])
