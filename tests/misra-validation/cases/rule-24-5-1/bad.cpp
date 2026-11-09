// Seeded violation: character classification with <cctype> and <cwctype>.
#include <cctype>
#include <cwctype>

namespace kv::rule_24_5_1::bad {

bool is_digit(char c) { return std::isdigit(static_cast<unsigned char>(c)) != 0; }

std::wint_t upper(std::wint_t c) { return std::towupper(c); }

}  // namespace kv::rule_24_5_1::bad
