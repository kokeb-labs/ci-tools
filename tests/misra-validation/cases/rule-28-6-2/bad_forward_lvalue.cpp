// Seeded violation: std::forward applied to a parameter that is not a forwarding reference (an lvalue reference).
#include <cstdint>
#include <utility>

namespace kv::rule_28_6_2::bad_forward_lvalue {

struct Payload {
  std::int32_t value;
};

std::int32_t consume(const Payload& payload) { return payload.value; }

std::int32_t consume(Payload&& payload) { return payload.value + 1; }

template <typename T>
std::int32_t relay(T& payload) {
  return consume(std::forward<T>(payload));  // seeded
}

std::int32_t use() {
  Payload p{1};
  return relay(p);
}

}  // namespace kv::rule_28_6_2::bad_forward_lvalue
