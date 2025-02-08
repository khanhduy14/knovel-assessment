CREATE TYPE public.role_enum AS ENUM (
    'employee',
    'employer'
);


ALTER TYPE public.role_enum OWNER TO postgres;

--
-- Name: task_status_enum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.task_status_enum AS ENUM (
    'pending',
    'in_progress',
    'completed'
);


ALTER TYPE public.task_status_enum OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: tasks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tasks (
    id uuid NOT NULL,
    title character varying NOT NULL,
    description character varying NOT NULL,
    status public.task_status_enum NOT NULL,
    created_at timestamp without time zone NOT NULL,
    due_date timestamp without time zone,
    assignee_id uuid NOT NULL,
    creator_id uuid NOT NULL,
    updated_at timestamp without time zone,
    updated_by uuid
);


ALTER TABLE public.tasks OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id uuid NOT NULL,
    username character varying NOT NULL,
    hashed_password character varying NOT NULL,
    role public.role_enum NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;
--
-- Data for Name: tasks; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tasks (id, title, description, status, created_at, due_date, assignee_id, creator_id, updated_at, updated_by) FROM stdin;
48b2db06-c0a0-4cea-a9db-6deb72e52668	test-task	test	pending	2025-02-08 14:14:58.980959	2025-12-12 00:00:00	5023b690-2295-4729-b843-677867a3d386	f3e44cfb-6f45-471d-85e2-795b1586dbde	\N	\N
b96644fb-6d62-4014-ac3f-9d081db97dd8	test-task	test	pending	2025-02-08 14:21:45.283174	2025-12-12 00:00:00	5023b690-2295-4729-b843-677867a3d386	f3e44cfb-6f45-471d-85e2-795b1586dbde	\N	\N
564f7f85-b111-4b48-a449-7172a8a182e1	test-task	test	pending	2025-02-08 14:22:38.185283	2025-12-12 00:00:00	5023b690-2295-4729-b843-677867a3d386	f3e44cfb-6f45-471d-85e2-795b1586dbde	\N	\N
a1dd6fa8-3eb2-4a7c-b8b3-70d3deaf3551	test-task	test	completed	2025-02-08 14:49:18.371134	2025-12-12 00:00:00	5023b690-2295-4729-b843-677867a3d386	f3e44cfb-6f45-471d-85e2-795b1586dbde	2025-02-08 14:52:17.842222	5023b690-2295-4729-b843-677867a3d386
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, username, hashed_password, role) FROM stdin;
f3e44cfb-6f45-471d-85e2-795b1586dbde	test-employer	$2b$12$wr8xIKIZ.pRwcXltJFuSMumEUUIfYYUoTHmEwXQ6kOo9kaVovkrCa	employer
5023b690-2295-4729-b843-677867a3d386	test-employee	$2b$12$LwfV4VZF5htrz2JcuqAg6uBOg8yopYpx.Mgt/xR1.OUhVVqwrzpIe	employee
\.


--
-- Name: tasks tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_tasks_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tasks_id ON public.tasks USING btree (id);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: ix_users_username; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_username ON public.users USING btree (username);


--
-- Name: tasks tasks_assignee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_assignee_id_fkey FOREIGN KEY (assignee_id) REFERENCES public.users(id);


--
-- Name: tasks tasks_creator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_creator_id_fkey FOREIGN KEY (creator_id) REFERENCES public.users(id);


--
-- Name: tasks tasks_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

