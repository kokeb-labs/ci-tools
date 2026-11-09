// Seeded violation: a local's address is stored in an object that outlives the local.
#include <cstdint>

namespace kv::rule_6_8_3::bad {

struct Holder {
  std::int32_t* target{nullptr};
};

void attach(Holder& holder) {
  std::int32_t local = 4;
  holder.target = &local;  // seeded
}

void publish(std::int32_t** out) {
  std::int32_t local = 5;
  *out = &local;  // seeded
}

}  // namespace kv::rule_6_8_3::bad
