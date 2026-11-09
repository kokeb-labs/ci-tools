// Seeded violation: public and protected data members in one struct.
#include <cstdint>

namespace kv::rule_14_1_1::bad_protected {

struct Limits {
  std::int32_t low = 0;

 protected:
  std::int32_t high = 0;
};

}  // namespace kv::rule_14_1_1::bad_protected
