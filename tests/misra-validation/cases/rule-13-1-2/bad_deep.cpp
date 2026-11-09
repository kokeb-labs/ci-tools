// Seeded violation (deep): a base reached virtually through one chain and non-virtually through a longer one.
#include <cstdint>

namespace kv::rule_13_1_2::bad_deep {

class Root {
 public:
  std::int32_t tag = 0;
};

class A : public virtual Root {};
class B : public Root {};
class C : public B {};
class Mix : public A, public C {};

std::int32_t size_hint() { return static_cast<std::int32_t>(sizeof(Mix)); }

}  // namespace kv::rule_13_1_2::bad_deep
