// Seeded violation: a helper type and function placed in the global namespace.
#include <cstdint>

struct KvRule603Point {  // seeded
  std::int32_t x{0};
};

std::int32_t kv_rule_6_0_3_origin_x() { return KvRule603Point{}.x; }  // seeded
