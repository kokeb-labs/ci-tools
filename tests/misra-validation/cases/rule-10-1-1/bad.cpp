// Seeded violation: a reference parameter that is only read is not const.
#include <cstdint>

namespace kv::rule_10_1_1::bad {

struct Sample {
  std::int32_t raw;
};

std::int32_t read_raw(Sample& s) {  // seeded
  return s.raw;
}

}  // namespace kv::rule_10_1_1::bad
