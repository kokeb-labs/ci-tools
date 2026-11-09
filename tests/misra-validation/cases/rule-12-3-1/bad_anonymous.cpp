// Seeded violation (anonymous): an anonymous union inside a struct.
#include <cstdint>

namespace kv::rule_12_3_1::bad_anonymous {

struct Value {
  bool is_int = true;
  union {  // seeded
    std::int32_t i;
    float f;
  };
};

std::int32_t as_int(const Value& v) { return v.is_int ? v.i : 0; }

}  // namespace kv::rule_12_3_1::bad_anonymous
