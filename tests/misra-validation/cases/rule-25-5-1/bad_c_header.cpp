// Seeded violation: setlocale through <locale.h>, unqualified, for one category.
#include <locale.h>

namespace kv::rule_25_5_1::bad_c_header {

void use_native_numbers() { static_cast<void>(setlocale(LC_NUMERIC, "")); }

}  // namespace kv::rule_25_5_1::bad_c_header
