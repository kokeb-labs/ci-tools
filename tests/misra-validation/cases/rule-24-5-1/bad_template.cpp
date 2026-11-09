// Seeded violation: isspace in a template and iswdigit in a lambda.
#include <cctype>
#include <cwctype>

namespace kv::rule_24_5_1::bad_template {

template <typename C>
bool blank(C c) {
  return std::isspace(static_cast<int>(c)) != 0;  // seeded
}

bool wide_digit(std::wint_t c) {
  const auto test = [](std::wint_t w) { return std::iswdigit(w) != 0; };  // seeded
  return test(c) || blank('x');
}

}  // namespace kv::rule_24_5_1::bad_template
