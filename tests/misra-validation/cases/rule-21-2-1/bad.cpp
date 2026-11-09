// Seeded violation: text converted with the ato* family, which cannot report a failed conversion.
#include <cstdint>
#include <cstdlib>

namespace kv::rule_21_2_1::bad {

std::int32_t parse_int(const char* text) { return std::atoi(text); }  // seeded

double parse_real(const char* text) { return std::atof(text); }  // seeded

}  // namespace kv::rule_21_2_1::bad
