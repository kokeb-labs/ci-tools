// Seeded violation of the claimed query (from the main case), so the case also proves detection.
#include <cstdint>

namespace kv::rule_6_7_2_variable_template::bad {

std::int32_t g_errors = 0;  // seeded

std::int32_t bump() {
  ++g_errors;
  return g_errors;
}

}  // namespace kv::rule_6_7_2_variable_template::bad
