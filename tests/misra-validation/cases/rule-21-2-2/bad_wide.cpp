// Seeded violation: the wide-character string functions.
#include <cstddef>
#include <cwchar>

namespace kv::rule_21_2_2::bad_wide {

std::size_t wide_length(const wchar_t* text) { return std::wcslen(text); }

unsigned long wide_number(const wchar_t* text) { return std::wcstoul(text, nullptr, 16); }

}  // namespace kv::rule_21_2_2::bad_wide
