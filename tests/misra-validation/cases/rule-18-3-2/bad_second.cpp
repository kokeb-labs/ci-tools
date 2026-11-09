// Seeded violation: the second handler takes a class type by value.
namespace kv::rule_18_3_2::bad_second {

struct Fault {
  int code = 0;
};

struct Timeout {
  int ms = 0;
};

int guard() {
  try {  // seeded: clang
    return 0;
  } catch (const Fault& f) {  // seeded: gcc
    return f.code;
  } catch (Timeout t) {
    return t.ms;
  }
}

}  // namespace kv::rule_18_3_2::bad_second
