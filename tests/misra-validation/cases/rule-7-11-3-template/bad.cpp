// Seeded violation of the claimed query (from the main case), so the case also proves detection.
#include <cstdint>

namespace kv::rule_7_11_3_template::bad {

std::int32_t one() { return 1; }

bool present() { return one != nullptr; }  // seeded

}  // namespace kv::rule_7_11_3_template::bad
